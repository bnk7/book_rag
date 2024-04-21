# code adapted from COSI 132A spring 2023

from sentence_transformers import SentenceTransformer
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import ScriptScore, Query

model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_query(q_vector: list[float]) -> Query:
    """
    generate an ES query that match all documents based on the cosine similarity

    :param q_vector: query embedding from the encoder
    :return: a query object
    """
    q_script = ScriptScore(
        query={"match_all": {}},  # use a match-all query
        script={  # script your scoring function
            "source": f"cosineSimilarity(params.q_vector, 'sbert_embedding') + 1.0",
            # add 1.0 to avoid negative score
            "params": {"q_vector": q_vector},
        },
    )
    return q_script


def search(index: str, query: Query, topk: int) -> list[dict]:
    """
    Create a query and return top k results

    :param index: index name
    :param query: ElasticSearch Query
    :param topk: number of hits to return
    :return: top k documents
    """
    # TODO: what is the 20?
    s = Search(using="default", index=index).query(query)[:20]
    response = s.execute()
    response_list = []
    for hit in response[:topk]:
        hit_dict = {'id': hit.meta.id, 'wikipedia_id': hit.wikipedia_id, 'freebase_id': hit.freebase_id,
                    'title': hit.title, 'author': hit.author, 'date': hit.date, 'genres': hit.genres,
                    'summary': hit.summary, 'score': hit.meta.score}
        response_list.append(hit_dict)
    return response_list


def process_query_and_search(query: str, index_name: str) -> list[dict]:
    """
    Given a user's query, returns the most relevant documents

    :param query: user's query
    :param index_name: name of the ElasticSearch index
    :return: top k documents
    """
    # get the query embedding and convert it to a list
    embeddings = model.encode([query])
    query_vector = embeddings.tolist()[0]
    # ElasticSearch Query scored with cosine similarity
    query_vector = generate_query(query_vector)
    # search
    return search(index_name, query_vector, 5)
