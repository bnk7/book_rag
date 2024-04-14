# https://elasticsearch-dsl.readthedocs.io/en/latest/
# code adapted from COSI 132A spring 2023
from sentence_transformers import SentenceTransformer
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import ScriptScore, Query


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


def search(index: str, query: Query, topk: int) -> None:
    # initialize a query and return top k results
    # TODO: what is the 20?
    s = Search(using="default", index=index).query(query)[:20]
    response = s.execute()
    for hit in response[:topk]:
        # print the document id that is assigned by ES index, score and title
        print(hit.meta.id, hit.doc_id, hit.meta.score, hit.title, sep="\t")
        # TODO: get the doc content - use BaseDoc fields
        # TODO: return instead of print


model = SentenceTransformer("all-MiniLM-L6-v2")
# TODO: get sentences from query. Segment them? Or keep as is?
sentences = ['sentence 1.', 'sentence2.']
embeddings = model.encode(sentences)

# get the query embedding and convert it to a list
query_vector = embeddings.tolist()[0]
# custom query that scores documents based on cosine similarity
query_vector = generate_query(query_vector)
# search, change the query object to see different results
search("nf_docs", query_vector, 5)
