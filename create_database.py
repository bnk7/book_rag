""" Code for creating the database"""

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
import numpy as np
import json
from alchemy_database import Base, add_book

if __name__ == '__main__':
    # read in book summaries from kaggle dataset found at
    # https://www.kaggle.com/datasets/ymaricar/cmu-book-summary-dataset
    df = pd.read_csv("booksummaries.txt", header=None, delimiter="\t", encoding='UTF8')
    df = df.rename(columns={
        0: 'wikipedia_id',
        1: 'freebase_id',
        2: 'title',
        3: 'author',
        4: 'pub_date',
        5: 'genres',
        6: 'summary'
    })
    df = df.replace({np.nan: None})
    print(df.head(3))

    # create database session
    DATABASE_URL = "sqlite:///books_db.db"
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # embedding model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    # add all books in the df to the database
    for index, row in df.iterrows():
        genres = None
        if row['genres'] is not None:
            genres = json.loads(row['genres'])
        add_book(model, db, row['title'], row['author'], genres, row['summary'], row['pub_date'])
