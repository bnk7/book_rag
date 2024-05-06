from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from string import Template
from llm_secret import key
from utils import dict_to_commas

api_key = key
model = "open-mistral-7b"

client = MistralClient(api_key=api_key)


def get_prompt(question: str, context: dict[str, str | dict[str, str]]) -> list[ChatMessage]:
    """Gets prompt for Mistral based on available information

    Args:
        question (str): user's question
        context (dict[str, str | dict[str, str]]): context from database related to question

    Returns:
        list[ChatMessage]: Mistral prompt
    """
    instruction = """Answer only the question asked; the response should be concise and relevant to the question."""

    prompt = """Context:\n""" + create_template_string(context) + f"""\n---\nNow here is the question you need to answer.\nQuestion: {question}"""

    message = [ChatMessage(role='system', content=instruction), ChatMessage(role='user', content=prompt)]
    return message


def create_template_string(context: dict) -> str:
    template_string = ""
    values = {'title': context['title'], 'summary': context['summary']}

    author_or_pub_date = context['author'] or context['pub_date']
    if author_or_pub_date:
        template_string = template_string + "$title was written"
    if context['author']:
        values['author'] = context['author']
        template_string = template_string + " by $author"
    if context['pub_date']:
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
    template_string = template_string + "Here is a summary of $title: $summary"

    prompt_template = Template(template_string)

    return prompt_template.substitute(values)


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
    Asks Mistral to choose the best book data out of the three returned by the retrieval system.

    Args:
        question (str) : The question posed by the user
        contexts (list[dict]) : The book data retrieved, len == 3

    Returns:
        The context dictionary representing the most salient book
    """
    instruction = "Answer only the question asked; the response should be concise and relevant to the question."
    prompt = ""
    for i, context in enumerate(contexts):
        if i == 0:
            prompt += "First Context:\n"
        elif i == 1:
            prompt += "Second Context:\n"
        elif i == 2:
            prompt += "Third Context:\n"
        prompt += create_template_string(context)
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
