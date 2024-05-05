from alchemy_database import process_query_and_search, make_book_db, make_book_df
from argparse import ArgumentParser
from falcon_evaluate.evaluate import FalconEvaluator
from falcon_evaluate.utils import MetricsAggregator
import json
from llm import get_answer
import pandas as pd
from rouge_score import rouge_scorer


DATABASE_URL = 'sqlite:///books_db.db'


def read_test_set(filepath: str) -> tuple[list[str], list[dict[str, str]], list[str]]:
    """Reads in test set from file

    Args:
        filepath (str): file containing test set

    Returns:
        tuple[list[str], list[dict[str, str]], list[str]]: lists of queries, ground truth contexts, and ground truth answers from test set
    """
    with open(filepath) as f:
        test_set = f.readlines()
    test_set = [json.loads(question) for question in test_set]
    queries = [data['question'] for data in test_set]
    true_contexts = test_set
    true_answers = [data['answer'] for data in test_set]
    return queries, true_contexts, true_answers


def run_pipeline(queries: list[str], book_df: pd.DataFrame) -> tuple[list[dict[str, str]], list[str]]:
    """Runs retrieval and generation pipeline on a set of queries

    Args:
        queries (list[str]): list of queries
        book_df (pd.DataFrame): dataframe containing book information

    Returns:
        tuple[list[dict[str, str]], list[str]]: lists of predicted contexts and predicted answers
    """
    predicted_contexts = []
    predicted_answers = []
    for query in queries:
        context = process_query_and_search(query, book_df)[0]
        answer = get_answer(query, context)
        predicted_contexts.append(context)
        predicted_answers.append(answer)
    return predicted_contexts, predicted_answers


def evaluate_contexts(true_contexts: list[dict[str, str]], predicted_contexts: list[dict[str, str]]) -> float:
    """Evaluates retrieval step of pipeline

    Args:
        true_contexts (list[dict[str, str]]): list of ground truth contexts for each query
        predicted_contexts (list[dict[str, str]]): list of predicted contexts for each query

    Returns:
        float: score representing retrieval performance
    """
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
    """Evaluates generation step of pipeline

    Args:
        queries (list[str]): list of queries
        true_answers (list[str]): list of ground truth answers for each query
        predicted_answers (list[str]): list of predicted answers for each query

    Returns:
        dict[str, float]: scores representing generation performance
    """
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
    book_df = make_book_df(db)
    
    queries, true_contexts, true_answers = read_test_set(args.filepath)
    predicted_contexts, predicted_answers = run_pipeline(queries, book_df)

    context_score = evaluate_contexts(true_contexts, predicted_contexts)
    answer_score = evaluate_answers(queries, true_answers, predicted_answers)

    print("Retrieval performance: " + str(context_score))
    print("Generation performance: " + str(answer_score))

    