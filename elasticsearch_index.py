# code adapted from COSI 132A spring 2023

import argparse
import json
import numpy as np
import os
import pandas as pd
from typing import Generator, Iterator, Sequence

from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Index
from elasticsearch_dsl import Document, Text, Keyword, DenseVector
from elasticsearch.helpers import bulk


def load_docs(data_dir_path: str | os.PathLike) -> Generator[dict]:
    """
    Prepare and load the documents for ES indexing

    :param data_dir_path: path to data
    :return: generator of JSON objects, one per document
    """
    # TODO: change to match embedding and data directory structure
    data_path = os.path.join(data_dir_path, 'data.csv')
    embeds_path = os.path.join(data_dir_path, 'docs_sb_mp_net_embeddings.npy')
    data_embeddings = np.load(str(embeds_path))
    df = pd.read_csv(data_path)
    df['sbert_embedding'] = df.index.apply(lambda x: data_embeddings[x].tolist())
    json_data = df.to_json(orient='records')
    for i, line in enumerate(json_data):
        yield json.loads(line)


class BaseDoc(Document):
    """
    document mapping structure
    """
    # treat the ID as a Keyword (its value won't be tokenized or normalized).
    wikipedia_id = Keyword()
    freebase_id = Keyword()
    # by default, Text field will be applied a standard analyzer at both index and search time
    title = Text()
    author = Text()
    date = Text()
    genres = Text()
    summary = Text()
    # sentence BERT embedding in the DenseVector field
    sbert_embedding = DenseVector(dims=768)


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
    def _populate_doc(docs: Iterator[dict] | Sequence[dict]) -> Generator[BaseDoc]:
        """
        Populate the BaseDoc

        :param docs: wapo docs
        :return: generator of documents
        """
        for i, doc in enumerate(docs):
            es_doc = BaseDoc(_id=i)
            es_doc.wikipedia_id = doc['Wikipedia ID']
            es_doc.freebase_id = doc['Freebase ID']
            es_doc.title = doc['Title']
            es_doc.author = doc['Author']
            es_doc.date = doc['Publication date']
            es_doc.genres = doc['Genres']
            es_doc.summary = doc['Summary']
            es_doc.sbert_embedding = doc["sbert_embedding"]  # TODO: change to match CSV
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
    def from_folder(cls, index_name: str, data_dir_path: str) -> "IndexLoader":
        try:
            return IndexLoader(index_name, load_docs(data_dir_path))
        except FileNotFoundError:
            raise Exception(f"Cannot find {data_dir_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index_name", required=True, type=str, help="name of the ES index")
    parser.add_argument("--data_dir_path", required=True, type=str, help="path to the data folder")
    args = parser.parse_args()

    idx_loader = IndexLoader.from_folder(args.index_name, args.data_dir_path)
    idx_loader.load()
