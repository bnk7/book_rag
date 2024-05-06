from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from string import Template
from llm_secret import key

api_key = key
model = "open-mistral-7b"

client = MistralClient(api_key=api_key)


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


def get_prompt(question: str, context: dict[str, str | dict[str, str]]) -> list[ChatMessage]:
    """Gets prompt for Mistral based on available information

    Args:
        question (str): user's question
        context (dict[str, str | dict[str, str]]): context from database related to question

    Returns:
        list[ChatMessage]: Mistral prompt
    """
    instruction = """Answer only the question asked; the response should be concise and relevant to the question."""
    values = {'title': context['title'],
              'summary': context['summary'], 'question': question}
    template_string = "Context:\n"
    author_or_pub_date = context['author'] is not None or context['pub_date'] is not None
    if author_or_pub_date:
        template_string = template_string + "$title was written"
    if context['author'] is not None:
        values['author'] = context['author']
        template_string = template_string + " by $author"
    if context['pub_date'] is not None:
        values['pub_date'] = context['pub_date'][:4]
        template_string = template_string + " in $pub_date"
    if author_or_pub_date:
        template_string = template_string + ". "
    if context['genres'] is not None:
        if author_or_pub_date:
            template_string = template_string + "It"
        else:
            template_string = template_string + "$title"
        values['genres'] = dict_to_commas(context['genres'])
        template_string = template_string + " is a work of $genres. "
    template_string = template_string + """Here is a summary of $title: $summary
---
Now here is the question you need to answer.
Question: $question"""

    prompt_template = Template(template_string)
    prompt = prompt_template.substitute(values)
    message = [ChatMessage(role='system', content=instruction),
               ChatMessage(role='user', content=prompt)]
    return message


def get_answer(question: str, context: dict[str, str | dict[str, str]]) -> str:
    """Gets Mistral output

    Args:
        question (str): user's question
        context (dict[str, str | dict[str, str]]): context related to question extracted from database

    Returns:
        str: Mistral output
    """
    message = get_prompt(question, context)
    chat_response = client.chat(
        model=model,
        messages=message,
    )
    return chat_response.choices[0].message.content


def choose_best_book(question: str, contexts: list[dict[str, str]]) -> dict[str, str | dict]:
    """

    """
    instruction = "Respond only to the question asked; the response should be concise and relevant to the question."
    prompt = """"""
    offset = 61 + len(question)
    for i, context in enumerate(contexts):
        doc_message = get_prompt(question, context)
        if i == 0:
            prompt += "First "
        elif i == 1:
            prompt += "Second "
        elif i == 2:
            prompt += "Third "
        prompt += doc_message[1].content[:-offset]
        prompt += "\n---------\n"
    prompt += f"""Based on these three contexts, which context (first, second, or third) most correctly answers the following question? 
Question: {question}
"""
    message = [ChatMessage(role='system', content=instruction), ChatMessage(role='user', content=prompt)]
    chat_response = client.chat(
        model=model,
        messages=message,
    )
    answer = chat_response.choices[0].message.content
    if "second" in answer:
        return contexts[1]
    elif "third" in answer:
        return contexts[2]
    else:
        return contexts[0]