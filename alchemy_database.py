import pickle
from sqlalchemy import create_engine, Column, Integer, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from llm import create_template_string
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer


Base = declarative_base()
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


class Book(Base):
    """
    Data model for all of the book information that is to be stored in a database.
    Contains a unique ID for each book, the book's title, author, genre(s), summary, publication date,
    and a numerical embedding of this data.
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


def make_book_df(db: Session) -> pd.DataFrame:
    """
    Given a database db and model, creates a pandas dataframe that includes equivalent information.
    Args:
        db (Session) : a database session

    Returns:
        DataFrame representing the equivalent data from the database
    """
    instances = db.query(Book).all()
    data = [{"id": instance.id,
             "title": instance.title,
             "author": instance.author,
             "genres": pickle.loads(instance.genres),
             "summary": instance.summary,
             "pub_date": instance.pub_date,
             "embedding": np.array(pickle.loads(instance.embedding))}
            for instance in instances]

    return pd.DataFrame(data)


def cosine_sim(x: np.ndarray, y: np.ndarray) -> float:
    """
    Computes the cosine similarity between vectors x and y.
    Args:
        x (numpy array): First vector
        y (numpy array): Second vector

    Returns:
        Numerical cosine similarity between the vectors
    """
    return np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))


def get_max_sim(data_df: pd.DataFrame, query_vec: np.ndarray) -> dict[str, str | dict]:
    """
    Returns the entry in the data_df that has an embedding that is most similar to the query vector.
    Args:
        data_df (pd.DataFrame): Dataframe containing embedding column of numpy array embedding vectors
        query_vec (numpy array): embedding vector representing the query

    Returns:
        Dictionary of row from data_df containing most similar information to the query vector
    """
    dot_products = data_df['embedding'].apply(lambda x: cosine_sim(x, query_vec))
    return dict(data_df.iloc[np.argmax(dot_products)])


def get_max_sims(data_df: pd.DataFrame, query_vec: np.ndarray, n: int) -> list[dict]:
    """
    Gets the n data_df dataframe entries that are most similar to the query vector.
    Args:
        data_df (pd.DataFrame): Dataframe containing embedding column of numpy array embedding vecs
        query_vec (numpy array): embedding vector representing the query
        n (int): number of most similar values to return

    Returns:
        List of dictionaries representing the data in the most similar rows to the query vector,
        ordered from most to least simiilar
    """
    data_df['sims'] = data_df['embedding'].apply(lambda x: cosine_sim(x, query_vec))
    return data_df.nlargest(n, 'sims').to_dict('records')


def add_book(model, db: Session, title: str, author: str, genres: dict[str, str], summary: str, pub_date: str):
    """
    Add book with given information to a sqlalchemy database, using the specified model.
    Args:
        model: SentenceTransformers model for encoding document embeddings
        db (Session): database for book to be added to
        title (str): book title
        author (str): book author
        genres (dict[str, str]): book genres
        summary (str): summary of book
        pub_date (str): book publication date
    """
    data = create_template_string({"title": title,
                                   "author": author,
                                   "genres": genres,
                                   "pub_date": pub_date,
                                   "summary": summary})
    embedding = np.array(model.encode(data))
    book = Book(title=title,
                author=author,
                genres=pickle.dumps(genres),
                summary=summary,
                pub_date=pub_date,
                embedding=pickle.dumps(embedding))
    db.add(book)
    db.commit()


def process_query_and_search(query: str, dataframe: pd.DataFrame, k: int = 1) -> list[dict]:
    """
    Given a user's query, returns the most relevant documents.
    Args:
        query (str) : user's query
        dataframe (pd.DataFrame) : name of dataframe to search
        k (int) : number of books to return, default 1
    Returns:
        List of book information dictionaries most similar to query
    """
    # get the query embedding and convert it to a list
    embeddings = model.encode([query])
    query_vector = np.array(embeddings[0])
    # search
    return get_max_sims(dataframe, query_vector, k)


def make_book_db(db_url: str) -> Session:
    """
    Returns database based on specific url.
    Args:
        db_url (str): url of requested database
    Returns:
        Database session
    """
    engine = create_engine(db_url, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    return db
