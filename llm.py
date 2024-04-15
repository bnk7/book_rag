import re
import torch
from transformers import pipeline
from string import Template

pipe = pipeline('text-generation', model='HuggingFaceH4/zephyr-7b-beta', torch_dtype=torch.bfloat16, device_map="auto")

def get_prompt(question: str, context: dict[str, str]) -> list[dict[str, str]]:
    """Gets prompt for Mistral based on available information

    Args:
        question (str): user's question
        context (dict[str, str]): context related to question extracted from database

    Returns:
        list[dict[str, str]]: Mistral prompt
    """
    values = {'title': context['title'], 'summary': context['summary'], 'question': question}
    if 'author' in context and 'genres' in context and 'date' in context:
        values['author'] = context['author']
        genres = list(context['genres'].values())
        if len(genres) > 1:
            values['genres'] = ', '.join(genres[:-1]) + ' and ' + genres[-1]
        else:
            values['genres'] = genres[0]
        values['date'] = context['date'][:4]
        prompt_template = Template('$title was written by $author in $date. It is a work of $genres. Here is a summary of $title: $summary\n$question')
    elif 'author' in context and 'genres' in context:
        values['author'] = context['author']
        genres = list(context['genres'].values())
        if len(genres) > 1:
            values['genres'] = ', '.join(genres[:-1]) + ' and ' + genres[-1]
        else:
            values['genres'] = genres[0]
        prompt_template = Template('$title was written by $author. It is a work of $genres. Here is a summary of $title: $summary\n$question')
    elif 'author' in context and 'date' in context:
        values['author'] = context['author']
        values['date'] = context['date'][:4]
        prompt_template = Template('$title was written by $author in $date. Here is a summary of $title: $summary\n$question')
    elif 'genres' in context and 'date' in context:
        genres = list(context['genres'].values())
        if len(genres) > 1:
            values['genres'] = ', '.join(genres[:-1]) + ' and ' + genres[-1]
        else:
            values['genres'] = genres[0]
        values['date'] = context['date'][:4]
        prompt_template = Template('$title was written in $date. It is a work of $genres. Here is a summary of $title: $summary\n$question')
    elif 'author' in context:
        values['author'] = context['author']
        prompt_template = Template('$title was written by $author. Here is a summary of $title: $summary\n$question')
    elif 'genres' in context:
        genres = list(context['genres'].values())
        if len(genres) > 1:
            values['genres'] = ', '.join(genres[:-1]) + ' and ' + genres[-1]
        else:
            values['genres'] = genres[0]
        prompt_template = Template('$title is a work of $genres. Here is a summary of $title: $summary\n$question')
    elif 'date' in context:
        values['date'] = context['date'][:4]
        prompt_template = Template('$title was written in $date. Here is a summary of $title: $summary\n$question')
    else:
        prompt_template = Template('Here is a summary of $title: $summary\n$question')
    
    prompt = prompt_template.substitute(values)
    message = [{'role': 'system', 'content': 'You are a trustworthy assistant for answering questions.'}, {'role': 'user', 'content': prompt}]
    return message

def get_answer(message: list[dict[str, str]]) -> str:
    """Gets Mistral output

    Args:
        message (list[dict[str, str]]): prompt for Mistral

    Returns:
        str: Mistral output
    """
    prompt = pipe.tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
    print(outputs[0]['generated_text'])


def extract_answer(output: str) -> str:
    """Extracts answer from Mistral output

    Args:
        output (str): Mistral output

    Returns:
        str: answer text
    """
    answer = re.search(r"\<\|assistant\|\>\s\"*([\S\s]*)\"*", output).group(1)
    return answer


if __name__ == '__main__':
    question = "Who is the main character of To Kill a Mockingbird?"
    context = {'title': 'To Kill a Mockingbird',
               'author': 'Harper Lee',
               'date': '1960-07-11',
               'genres': {"/m/02xlf": "Fiction"},
               'summary':  'The book opens with the Finch family\'s ancestor, Simon Finch, a Cornish Methodist fleeing religious intolerance in England, settling in Alabama, becoming wealthy and, contrary to his religious beliefs, buying several slaves. The main story takes place during three years of the Great Depression in the fictional "tired old town" of Maycomb, Alabama. It focuses on six-year-old Scout Finch, who lives with her older brother Jem and their widowed father Atticus, a middle-aged lawyer. Jem and Scout befriend a boy named Dill who visits Maycomb to stay with his aunt each summer. The three children are terrified of, and fascinated by, their neighbor, the reclusive "Boo" Radley. The adults of Maycomb are hesitant to talk about Boo and for many years few have seen him. The children feed each other\'s imagination with rumors about his appearance and reasons for remaining hidden, and they fantasize about how to get him out of his house. Following two summers of friendship with Dill, Scout and Jem find that someone is leaving them small gifts in a tree outside the Radley place. Several times, the mysterious Boo makes gestures of affection to the children, but, to their disappointment, never appears in person. Atticus is appointed by the court to defend Tom Robinson, a black man who has been accused of raping a young white woman, Mayella Ewell. Although many of Maycomb\'s citizens disapprove, Atticus agrees to defend Tom. Other children taunt Jem and Scout for Atticus\' actions, calling him a "nigger-lover". Scout is tempted to stand up for her father\'s honor by fighting even though he has told her not to. For his part, Atticus faces a group of men intent on lynching Tom. This danger is averted when Scout, Jem, and Dill shame the mob into dispersing by forcing them to view the situation from Atticus\' and Tom\'s points of view. Because Atticus does not want them to be present at Tom Robinson\'s trial, Scout, Jem and Dill watch in secret from the colored balcony. Atticus establishes that the accusers—Mayella and her father, Bob Ewell, the town drunk—are lying. It also becomes clear that the friendless Mayella was making sexual advances towards Tom and her father caught her and beat her. Despite significant evidence of Tom\'s innocence, the jury convicts him. Jem\'s faith in justice is badly shaken, as is Atticus\', when a hopeless Tom is shot and killed while trying to escape from prison. Humiliated by the trial Bob Ewell vows revenge. He spits in Atticus\' face on the street, tries to break into the presiding judge\'s house and menaces Tom Robinson\'s widow. Finally, he attacks the defenseless Jem and Scout as they walk home on a dark night from the school Halloween pageant. Jem\'s arm is broken in the struggle, but amid the confusion, someone comes to the children\'s rescue. The mysterious man carries Jem home, where Scout realizes that he is Boo Radley. Maycomb\'s sheriff arrives and discovers that Bob Ewell has been killed in the struggle. The sheriff argues with Atticus about the prudence and ethics of holding Jem or Boo responsible. Atticus eventually accepts the sheriff\'s story that Ewell simply fell on his own knife. Boo asks Scout to walk him home, and after she says goodbye to him at his front door, he disappears again. While standing on the Radley porch, Scout imagines life from Boo\'s perspective and regrets that they never repaid him for the gifts he had given them.'}
    get_answer(get_prompt(question, context))