from alchemy_database import process_query_and_search, make_book_db, make_book_df, Book
from argparse import ArgumentParser
from falcon_evaluate.evaluate import FalconEvaluator
from falcon_evaluate.utils import MetricsAggregator
import json
from llm import get_prompt, get_answer
import pandas as pd
from rouge_score import rouge_scorer


DATABASE_URL = 'sqlite:///books_db.db'


def read_test_set(filepath: str) -> tuple[list[str], list[dict[str, str]], list[str]]:
    """
    """
    with open(filepath) as f:
        test_set = f.readlines()
    test_set = [json.loads(question) for question in test_set]
    queries = [data['question'] for data in test_set]
    true_contexts = test_set
    true_answers = [data['answer'] for data in test_set]
    return queries, true_contexts, true_answers


def run_pipeline(queries: list[str], df: pd.DataFrame) -> tuple[list[dict[str, str], list[str]]]:
    predicted_contexts = []
    predicted_answers = []
    for query in queries:
        context = process_query_and_search(query, df)[0]
        answer = get_answer(get_prompt(query, context))
        predicted_contexts.append(context)
        predicted_answers.append(answer)
    return predicted_contexts, predicted_answers


def evaluate_contexts(true_contexts: list[dict[str, str]], predicted_contexts: list[dict[str, str]]) -> float:
    # adjust these weights to determine how much each component of the context should contribute to the overall score
    weights = {'title': 0.45, 'author': 0.25, 'summary': 0.3}
    # using rouge2 score currently, but can be adjusted to another rougeN or rougeL
    scorer = rouge_scorer.RougeScorer(['rouge2'])
    scores = []
    for true, predicted in zip(true_contexts, predicted_contexts):
        score = 0
        if true['title'] == predicted['title']:
            score += 1 * weights['title']
        if true['author'] == predicted['author']:
            score += 1 * weights['author']
        rouge = scorer.score(true['summary'], predicted['summary'])['rouge2'].fmeasure
        score += rouge * weights['summary']
        scores.append(score)
    return sum(scores) / len(scores)


def evaluate_answers(queries: list[str], true_answers: list[str], predicted_answers: list[str]) -> dict[str, float]:
    df = pd.DataFrame({'prompt': queries, 'reference': true_answers, 'Mistral': predicted_answers})
    evaluator = FalconEvaluator(df)
    evaluation_results = evaluator.evaluate(use_relevance=False)
    aggregator = MetricsAggregator(evaluation_results)
    aggregated_metrics_df = aggregator.aggregate()
    scores = aggregated_metrics_df['Mistral-Scores'][0]['Text Similarity and Relevance']
    return scores


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--filepath', help='the file containing the test set', default='test_questions.jsonl')
    args = parser.parse_args()

    db = make_book_db(DATABASE_URL)
    book_df = make_book_df(db, Book)
    
    queries, true_contexts, true_answers = read_test_set(args.filepath)
    predicted_contexts, predicted_answers = run_pipeline(queries, book_df)

    context_score = evaluate_contexts(true_contexts, predicted_contexts)
    answer_score = evaluate_answers(queries, true_answers, predicted_answers)

    with open('test_contexts.json', 'w') as f:
        json.dump([{'title': context['title'], 'author': context['author'], 'pub_date': context['pub_date'], 'genres': context['genres'], 'summary': context['summary']} for context in predicted_contexts], f)
    
    with open('test_answers.json', 'w') as f:
        json.dump(predicted_answers, f)

    print(context_score)
    print(answer_score)

    