# code adapted from COSI 132A spring 2023

import argparse
import json
from typing import Generator, Iterator, Sequence
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Index
from elasticsearch_dsl import Document, Text, Keyword, DenseVector
from elasticsearch.helpers import bulk

from alchemy_database import make_book_df, Book, Base


def load_docs() -> Generator[dict, None, None]:
    """
    Prepare and load the documents for ES indexing

    :return: generator of JSON objects, one per document
    """
    DATABASE_URL = "sqlite:///books_db.db"
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    df = make_book_df(db, Book)
    json_data = df.to_json(orient='records')
    for i, line in enumerate(json_data):
        yield json.loads(line)


class BaseDoc(Document):
    """
    document mapping structure
    """
    # treat the ID as a Keyword (its value won't be tokenized or normalized).
    id = Keyword()
    # by default, Text field will be applied a standard analyzer at both index and search time
    title = Text()
    author = Text()
    pub_date = Text()
    genres = Text()
    summary = Text()
    # sentence BERT embedding in the DenseVector field
    embedding = DenseVector(dims=768)


class ESIndex(object):
    def __init__(self, index_name: str, docs: Iterator[dict] | Sequence[dict]):
        """
        ES index structure

        :param index_name: the name of the index
        :param docs: data to be loaded
        """
        # set an elasticsearch connection to your localhost
        connections.create_connection(hosts=["localhost"], timeout=100, alias="default")
        self.index = index_name
        es_index = Index(self.index)  # initialize the index

        # delete existing index that has the same name
        if es_index.exists():
            es_index.delete()

        es_index.document(BaseDoc)  # link document mapping to the index
        es_index.create()  # create the index, still empty at this point
        if docs is not None:
            self.load(docs)

    @staticmethod
    def _populate_doc(docs: Iterator[dict] | Sequence[dict]) -> Generator[BaseDoc, None, None]:
        """
        Populate the BaseDoc

        :param docs: documents
        :return: generator of documents
        """
        for doc in docs:
            es_doc = BaseDoc(_id=doc['id'])
            es_doc.title = doc['title']
            es_doc.author = doc['author']
            es_doc.pub_date = doc['pub_date']
            es_doc.genres = doc['genres']
            es_doc.summary = doc['summary']
            es_doc.embedding = doc['embedding']
            yield es_doc

    def load(self, docs: Iterator[dict] | Sequence[dict]) -> None:
        """
        Perform bulk insertion

        :param docs: documents to be inserted
        :return: None
        """
        bulk(
            connections.get_connection(),
            (
                # serialize the BaseDoc instance (include meta information and not skip empty documents)
                d.to_dict(include_meta=True, skip_empty=False)
                for d in self._populate_doc(docs)
            ),
        )


class IndexLoader:
    """
    load document index to Elasticsearch
    """
    def __init__(self, index: str, docs: Iterator[dict] | list[dict]):
        self.index_name = index
        self.docs = docs

    def load(self) -> None:
        print('Building index ...')
        ESIndex(self.index_name, self.docs)

    @classmethod
    def from_alchemy(cls, index_name: str) -> "IndexLoader":
        return IndexLoader(index_name, load_docs())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index_name", required=True, type=str, help="name of the ES index")
    args = parser.parse_args()

    idx_loader = IndexLoader.from_alchemy(args.index_name)
    idx_loader.load()
