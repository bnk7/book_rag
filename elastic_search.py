# code adapted from COSI 132A spring 2023

from sentence_transformers import SentenceTransformer
from elasticsearch_dsl import Search, connections
from elasticsearch_dsl.query import ScriptScore, Query

# set an elasticsearch connection to your localhost
with open('es_password.txt') as f:
    es_password = f.readline().strip()
connections.create_connection(hosts=['https://localhost:9200'], timeout=100, alias="default",
                              basic_auth=('elastic', es_password), verify_certs=False)

model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_query(q_vector: list[float], scoring_function: str) -> Query:
    """
    Generate an ES query that matches documents based on the given scoring function

    :param q_vector: query embedding from the encoder
    :param scoring_function: cosineSimilarity, dotProduct, l1norm, or l2norm
    :return: a query object
    """
    q_script = ScriptScore(
        query={"match_all": {}},  # use a match-all query
        script={  # script your scoring function
            "source": f"{scoring_function}(params.q_vector, 'embedding') + 1.0",
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
    s = Search(using="default", index=index).query(query)[:20]
    response = s.execute()
    response_list = []
    for hit in response[:topk]:
        hit_dict = {'id': int(hit.meta.id), 'title': hit.title, 'author': hit.author, 'pub_date': hit.pub_date,
                    'genres': hit.genres, 'summary': hit.summary, 'score': hit.meta.score}
        response_list.append(hit_dict)
    return response_list


def process_query_and_search(query: str, index_name: str, k: int = 1, scoring_function: str = 'cosineSimilarity') \
        -> list[dict]:
    """
    Given a user's query, returns the most relevant documents

    :param query: user's query
    :param index_name: name of the ElasticSearch index
    :param k: number of books to return
    :param scoring_function: cosineSimilarity, dotProduct, l1norm, or l2norm
    :return: top k documents
    """
    # get the query embedding and convert it to a list
    embeddings = model.encode([query])
    query_vector = embeddings.tolist()[0]
    # ElasticSearch Query scored with specified function
    query_vector = generate_query(query_vector, scoring_function)
    # search
    return search(index_name, query_vector, k)


if __name__ == '__main__':
    user_input = "Where are the characters of Dr. Franklin’s Island by Gwyneth Jones headed when their plane crashes?"
    results = process_query_and_search(user_input, 'books', k=2)
    print('RESULTS:')
    print(results)
