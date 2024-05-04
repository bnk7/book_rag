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
        genres = list(context['genres'].values())
        if len(genres) > 1:
            values['genres'] = ', '.join(genres[:-1]) + ' and ' + genres[-1]
        else:
            values['genres'] = genres[0]
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
