# code adapted from COSI 132A spring 2023

import argparse
import json
import numpy as np
import os
import pandas as pd
from typing import Generator, Iterator, Sequence

from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Index
from elasticsearch_dsl import Document, Text, Keyword, Nested, DenseVector
from elasticsearch.helpers import bulk


def load_docs(data_dir_path: str | os.PathLike) -> Generator[dict]:
    # prepare and load the documents for ES indexing
    # TODO: does the modified function work?
    data_path = os.path.join(data_dir_path, 'data.csv')
    # TODO: where/how are these embeddings created?
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
    # treat the doc_id as a Keyword (its value won't be tokenized or normalized).
    doc_id = Keyword()
    # TODO: change this to match the CSV columns - could do one per col or Nested
    # by default, Text field will be applied a standard analyzer at both index and search time
    title = Text()
    content = Text()
    # sentence BERT embedding in the DenseVector field
    sbert_embedding = DenseVector(dims=768)


class ESIndex(object):
    def __init__(self, index_name: str, docs: Iterator[dict] | Sequence[dict]):
        """
        ES index structure
        :param index_name: the name of your index
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
        populate the BaseDoc
        :param docs: wapo docs
        :return:
        """
        for i, doc in enumerate(docs):
            es_doc = BaseDoc(_id=i)
            # TODO: change this to match the CSV columns
            es_doc.doc_id = doc["_id"]
            es_doc.title = doc["title"]
            es_doc.content = doc["text"]
            es_doc.sbert_embedding = doc["sbert_embedding"]
            yield es_doc

    def load(self, docs: Iterator[dict] | Sequence[dict]):
        # bulk insertion
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
    def __init__(self, index, docs: Iterator[dict] | list[dict]):
        self.index_name = index
        self.docs = docs

    def load(self) -> None:
        print('Building index ...')
        ESIndex(self.index_name, self.docs)

    @classmethod
    def from_folder(cls, index_name: str, nf_folder_path: str) -> "IndexLoader":
        try:
            return IndexLoader(index_name, load_docs(nf_folder_path))
        except FileNotFoundError:
            raise Exception(f"Cannot find {nf_folder_path}!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index_name", required=True, type=str, help="name of the ES index")
    parser.add_argument("--data_dir_path", required=True, type=str, help="path to the data folder")
    args = parser.parse_args()

    idx_loader = IndexLoader.from_folder(args.index_name, args.data_dir_path)
    idx_loader.load()
