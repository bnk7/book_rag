from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from string import Template
from llm_secret import key

api_key = key
model = "open-mistral-7b"

client = MistralClient(api_key=api_key)


def get_prompt(question: str, context: dict[str, str | dict]) -> list[ChatMessage]:
    """Gets prompt for Mistral based on available information

    Args:
        question (str): user's question
        context (dict[str, str]): context related to question extracted from database

    Returns:
        list[ChatMessage]: Mistral prompt
    """
    instruction = """Respond only to the question asked; the response should be concise and relevant to the question."""
    values = {'title': context['title'], 'summary': context['summary'], 'question': question}
    template_string = """Here is a summary of $title: $summary
---
Now here is the question you need to answer. 
Question: $question"""

    has_author = context["author"] is not None
    if has_author:
        values['author'] = context['author']
        template_string = "$title was written by $author. " + template_string
    if context['pub_date'] is not None:
        values['pub_date'] = context['pub_date'][:4]
        if has_author:
            template_string = template_string[:29] + " in $pub_date" + template_string[29:]
        else:
            template_string = "$title was written in $pub_date. " + template_string
    if context['genres'] is not None:
        values['genres'] = dict_to_commas(context["genres"])
        if has_author:
            template_string = template_string[:-107] + "It is a work of $genres. " + template_string[-107:]
        else:
            if "date" in template_string:
                template_string = template_string[:33] + "It is a work of $genres. " + template_string[33:]
            else:
                template_string = "$title is a work of $genres. " + template_string

    template_string = """Context:\n""" + template_string

    prompt_template = Template(template_string)
    prompt = prompt_template.substitute(values)
    message = [ChatMessage(role='system', content=instruction), ChatMessage(role='user', content=prompt)]
    return message


def dict_to_commas(data: dict[str, str]) -> str:
    """
    Return a nicely formatted readable version of the values of a dictionary.

    Args:
        data (dict[str, str]): The dictionary to be formatted
    Returns:
        String representing the values of the dictionary
    """
    items = list(data.values())
    if len(items) > 2:
        output = ', '.join(items[:-1]) + ', and ' + items[-1]
    elif len(items) == 2:
        output = items[0] + ' and ' + items[1]
    else:
        output = items[0]
    return output


def convert_date(date: str) -> str:
    """Converts the given date from yyyy-mm-dd format to month day, year format.

    Args:
        date (str): The date to convert
    Returns:
        String representing the reformatted date
    """
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    year = date[:4]
    month = months[int(date[5:7])]
    day = date[-2:]

    return month + " " + day + ", " + year


def get_answer(question, context) -> str:
    """Gets Mistral output

    Args:
        question (str): user's question
        context (dict[str, str]): context related to question extracted from database

    Returns:
        str: Mistral output
    """
    message = get_prompt(question, context)
    chat_response = client.chat(
        model=model,
        messages=message,
    )
    return chat_response.choices[0].message.content
