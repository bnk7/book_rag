import pickle
from sqlalchemy import create_engine, Column, Integer, String, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer


Base = declarative_base()
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


class Book(Base):
    """
    data model for all of the book information that is to be stored in a database
    """
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, unique=True, index=True)
    title = Column(Text)
    author = Column(Text)
    genres = Column(LargeBinary)  # dictionary
    summary = Column(Text)
    pub_date = Column(Text)
    embedding = Column(LargeBinary)  # np array

    def __repr__(self):
        return f"('{self.title}')"


# makes a dataframe out of book database
def make_book_df(db):
    """
    given a database db and model, it creates a pandas dataframe that
    includes all of the same values
    Args:
        db: a database session

    Returns: pandas dataframe

    """
    instances = db.query(Book).all()
    data = [{"id": instance.id, "title": instance.title, "author": instance.author,
             "genres": pickle.loads(instance.genres), "summary": instance.summary, "pub_date": instance.pub_date,
             "embedding": np.array(pickle.loads(instance.embedding))} for instance in instances]
    return pd.DataFrame(data)


def cosine_sim(x, y):
    """
    computes the cosine similarity between vectors x and y
    Args:
        x: numpy array
        y: numpy array

    Returns: numerical cosine similarity

    """
    return np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))


# gets the most similar document to query_vec from data_df
def get_max_sim(data_df, query_vec):
    """
    returns the entry in the data_df that has an embedding that is most similar to the query vec
    Args:
        data_df: pandas df that contains embedding column of numpy array embedding vecs
        query_vec: numpy array vector

    Returns: dict of most similar information from data_df

    """
    dot_products = data_df['embedding'].apply(lambda x: cosine_sim(x, query_vec))  # np.dot(data_df['embedding'], query_vec)
    return dict(data_df.iloc[np.argmax(dot_products)])


# gets n most similar documents to query_vec from data_df
def get_max_sims(data_df, query_vec, n):
    """
    gets the data_df dataframe entries that are most similar to the query vector
    Args:
        data_df: pandas df that contains embedding column of numpy array embedding vecs
        query_vec: numpy array vector
        n: number of most similar values to return

    Returns: list of dicts

    """
    data_df['sims'] = data_df['embedding'].apply(lambda x: cosine_sim(x, query_vec))  # np.dot(data_df['embedding'], query_vec)
    return data_df.nlargest(n, 'sims').to_dict('records')


# helper method for making comma separated strings out of dictionaries
def make_comma_sep_string(items: dict):
    """
    turns a dictionary of strings into a string in a comma separated
    natural langauge list format
    Args:
        items: a dictionary of strings

    Returns: string formatted with commas and 'and'

    """
    str_list = ''
    items_list = list(items.values())
    if len(items_list) > 1:
        str_list = ', '.join(items_list[:-1]) + ' and ' + items_list[-1]
    else:
        str_list = items_list[0]
    return str_list


# gets the prompt to be fed into the embedding model
def emb_get_prompt(title, author, genres, summary, pub_date):
    """
    gets a prompt that contains book information all together in a
    natural langauge prompt
    Args:
        title: string book title
        author: string author
        genres: dict of genres
        summary: string summary of book
        pub_date: string date

    Returns: string that contains all book information together

    """
    prompt = title + " was written"
    if author:
        prompt += " by " + author
    if pub_date:
        prompt += " in " + pub_date
    prompt += "."
    if genres:
        prompt += " It is a work of " + make_comma_sep_string(genres)+"."
    if summary:
        prompt += " Here is a summary of " + title + ": " + summary
    return prompt


def add_book(model, db, title: str, author: str, genres: dict, summary: str, pub_date: str):
    """
    Add book to a sqlalchemy database
    Args:
        model: model for encoding document embeddings
        db: database for book to be added to
        title: string book title
        author: string author
        genres: dict of genres
        summary: string summary of book
        pub_date: string date

    """
    data = emb_get_prompt(title, author, genres, summary, pub_date)
    embedding = np.array(model.encode(data))
    book = Book(title=title, author=author, genres=pickle.dumps(genres), summary=summary, pub_date=pub_date, embedding=pickle.dumps(embedding))
    db.add(book)
    db.commit()


def process_query_and_search(query: str, dataframe: pd.DataFrame, k: int = 1) -> list[dict]:
    """
    Given a user's query, returns the most relevant documents

    :param query: user's query
    :param dataframe: name of dataframe to search
    :param k: number of books to return
    :return: top k documents
    """
    # get the query embedding and convert it to a list
    embeddings = model.encode([query])
    query_vector = np.array(embeddings[0])
    # search
    return get_max_sims(dataframe, query_vector, k)


def make_book_db(db_url: str):
    """
    returns database based on specific url
    Args:
        db_url: string database url

    Returns: database

    """
    engine = create_engine(db_url, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    return db


def get_prompt_from_dict(doc: dict, question: str = None):
    """
    given a dict (doc) of book information and optionally a question
    it returns this information together in a string in a specific  format
    Args:
        doc: dictionary that contains all document information
            (assumes that title exists, but other values can be None)
        question: question string

    Returns: prompt string

    """
    prompt = emb_get_prompt(doc['title'], doc['author'], doc['genres'], doc['summary'], doc['pub_date'])
    if question:
        prompt += '\n' + question
    return prompt


if __name__ == "__main__":
    DATABASE_URL = "sqlite:///books_db.db"
    db = make_book_db(DATABASE_URL)
    book_df = make_book_df(db)
    question = "What does the dagger symbolize in Macbeth?"
    # retrieved docs as list of dicts
    docs = process_query_and_search(question, book_df, 3)  # list of dicts
    # keys in each doc are ['id', 'title', 'author', 'genres', 'summary', 'pub_date', 'embedding', 'sims']
    # print out the results from the retrieved docs title, author, and start of prompt
    for doc in docs:
        # print title and author of retrieved docs
        print("----------------")
        print(doc['title'])
        print(doc['author'])
        print(get_prompt_from_dict(doc, question)[:50])  # prints out beginning of prompt
        print(get_prompt_from_dict(doc, question)[-50:])  # prints out last part of prompt to show question

