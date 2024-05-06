from alchemy_database import *
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
    pred_contexts = []
    pred_answers = []
    for query in queries:
        context = process_query_and_search(query, book_df)[0]
        answer = get_answer(query, context)
        pred_contexts.append(context)
        pred_answers.append(answer)
    return pred_contexts, pred_answers


def evaluate_contexts(true_contexts: list[dict[str, str]], pred_contexts: list[dict[str, str]]) -> float:
    """Evaluates retrieval step of pipeline

    Args:
        true_contexts (list[dict[str, str]]): list of ground truth contexts for each query
        pred_contextes (list[dict[str, str]]): list of predicted contexts for each query

    Returns:
        float: score representing retrieval performance
    """
    # these weights determine how much each component of the context contributes to the overall score
    weights = {'title': 0.45, 'author': 0.25, 'summary': 0.3}
    scorer = rouge_scorer.RougeScorer(['rouge2'])
    scores = []
    for true, pred in zip(true_contexts, pred_contexts):
        score = 0
        if true['title'] == pred['title']:
            score += 1 * weights['title']
        if true['author'] == pred['author']:
            score += 1 * weights['author']
        rouge_scores = scorer.score(true['summary'], pred['summary'])
        rouge = rouge_scores['rouge2'].fmeasure
        score += rouge * weights['summary']
        scores.append(score)
    return sum(scores) / len(scores)


def evaluate_answers(queries: list[str], true_answers: list[str], pred_answers: list[str]) -> float:
    """Evaluates generation step of pipeline

    Args:
        queries (list[str]): list of queries
        true_answers (list[str]): list of ground truth answers for each query
        pred_answers (list[str]): list of predicted answers for each query

    Returns:
        float: score representing generation performance
    """
    df = pd.DataFrame({'prompt': queries,
                       'reference': true_answers,
                       'Mistral': pred_answers})
    evaluator = FalconEvaluator(df)
    evaluation_results = evaluator.evaluate(use_relevance=False)
    aggregator = MetricsAggregator(evaluation_results)
    aggregated_metrics = aggregator.aggregate()
    scores = aggregated_metrics['Mistral-Scores'][0]
    similarity = scores['Text Similarity and Relevance']['Jaccard Similarity']
    return similarity


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--filepath',
                        help='the file containing the test set',
                        default='test_questions.jsonl')
    args = parser.parse_args()

    db = make_book_db(DATABASE_URL)
    book_df = make_book_df(db)

    queries, true_contexts, true_answers = read_test_set(args.filepath)
    pred_contexts, pred_answers = run_pipeline(queries, book_df)

    context_score = evaluate_contexts(true_contexts, pred_contexts)
    answer_score = evaluate_answers(queries, true_answers, pred_answers)

    print("Retrieval performance: " + str(context_score))
    print("Generation performance: " + str(answer_score))
