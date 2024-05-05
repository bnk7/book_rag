import unittest
import elastic_search
import alchemy_database
import elasticsearch_index

DATABASE_URL = "sqlite:///books_db.db"
db = alchemy_database.make_book_db(DATABASE_URL)
book_df = alchemy_database.make_book_df(db)
elasticsearch_index.load_es_index()


class TestOutput(unittest.TestCase):
    def test_query(self):
        q = "Where are the characters of Dr. Franklin’s Island by Gwyneth Jones headed when their plane crashes?"
        es_output = elastic_search.process_query_and_search(q, 'books')
        al_output = alchemy_database.process_query_and_search(q, book_df)
        for i, book in enumerate(al_output):
            for field in ['id', 'title', 'author', 'pub_date', 'genres', 'summary']:
                self.assertEqual(es_output[i][field], al_output[i][field])


if __name__ == '__main__':
    unittest.main()
