import unittest
import numpy as np
import pickle
import pandas as pd
from llm import dict_to_commas
from alchemy_database import Book, make_book_db, add_book, make_book_df, \
    cosine_sim, get_max_sim, get_max_sims


# Define the unit tests
class TestBookClass(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # This is just a placeholder for the LLM model encode method
        class Model:
            def encode(self, data):
                return [1, 2, 3]  # Sample embedding

        self.db = make_book_db("sqlite:///:memory:")
        # add sample books to the database
        add_book(Model(), self.db, "Title 1", "Author 1", {"Genre": "Fiction"}, "Summary 1", "2022-01-01")
        add_book(Model(), self.db, "Title 2", "Author 2", {"Genre": "Non-Fiction"}, "Summary 2", "2022-01-02")

    def test_book_repr(self):
        # create a sample book object
        book = Book(title="Sample Title")
        # check if the repr method returns the expected string
        self.assertEqual(repr(book), "('Sample Title')")

    def test_make_book_db(self):
        # Test the make_book_db function
        # Check if the database session is created successfully
        self.assertIsNotNone(self.db)

    def test_add_book(self):
        # This is just a placeholder for the LLM model encode method
        class Model:
            def encode(self, data):
                return [1, 2, 3]  # Sample embedding

        # add a sample book
        add_book(Model(), self.db, "Title", "Author", {"Genre": "Fiction"}, "Summary", "2022-01-01")
        # retrieve the added book from the database
        added_book = self.db.query(Book).filter_by(title="Title").first()
        # check if the book was added successfully
        self.assertIsNotNone(added_book)
        # check if the book's attributes match the provided values
        self.assertEqual(added_book.title, "Title")
        self.assertEqual(added_book.author, "Author")
        self.assertEqual(pickle.loads(added_book.genres), {"Genre": "Fiction"})
        self.assertEqual(added_book.summary, "Summary")
        self.assertEqual(added_book.pub_date, "2022-01-01")
        # check if the embedding was added successfully
        expected_embedding = np.array([1, 2, 3])
        actual_embedding = pickle.loads(added_book.embedding)
        self.assertTrue(np.array_equal(actual_embedding, expected_embedding))

    def test_make_book_df(self):
        # call make_book_df to convert database records to dataframe
        df = make_book_df(self.db)

        # check if df is not empty
        self.assertFalse(df.empty)

        # check if df columns are as expected
        expected_columns = ["id", "title", "author", "genres", "summary", "pub_date", "embedding"]
        self.assertEqual(list(df.columns), expected_columns)

        # check if embedding column contains np arrays
        self.assertTrue(all(isinstance(embedding, np.ndarray) for embedding in df["embedding"]))
        # check if genres column has dicts
        self.assertTrue(all(isinstance(embedding, dict) for embedding in df["genres"]))


class TestMethods(unittest.TestCase):
    def setUp(self):
        # mock df
        self.df = pd.DataFrame({
            'title': ['Book 1', 'Book 2', 'Book 3'],
            'author': ['Author 1', 'Author 2', 'Author 3'],
            'genres': [{'g': 'Fiction'}, {'g': 'Non-Fiction'}, {'g': 'Fantasy'}],
            'summary': ['Summary 1', 'Summary 2', 'Summary 3'],
            'pub_date': ['2022-01-01', '2022-01-02', '2022-01-03'],
            'embedding': [[1, 0, 0], [1, 0, 1], [1, 0, 0]]  # mock embeddings
        })

    def test_make_comma_sep_string(self):
        # test with three genres
        result = dict_to_commas({'genre1': 'Fiction', 'genre2': 'Fantasy', 'genre': 'SciFi'})
        self.assertEqual(result, 'Fiction, Fantasy, and SciFi')

        # test with two genres
        result = dict_to_commas({'genre1': 'Fiction', 'genre2': 'Fantasy'})
        self.assertEqual(result, 'Fiction and Fantasy')

        # test with single genre
        result = dict_to_commas({'genre1': 'Fiction'})
        self.assertEqual(result, 'Fiction')

    def test_cosine_sim(self):
        x = np.array([1, 0, 0])
        y = np.array([1, 0, 0])
        result = cosine_sim(x, y)
        self.assertAlmostEqual(result, 1.0, places=8)

        x = np.array([1, 0, 0])
        y = np.array([0, 1, 0])
        result = cosine_sim(x, y)
        self.assertAlmostEqual(result, 0.0, places=8)

    def test_get_max_sim(self):
        query_vec = np.array([1, 0, 1])
        result = get_max_sim(self.df, query_vec)
        expected = {'title': 'Book 2',
                    'author': 'Author 2',
                    'genres': {'g': 'Non-Fiction'},
                    'summary': 'Summary 2',
                    'pub_date': '2022-01-02',
                    'embedding': [1, 0, 1]}
        self.assertDictEqual(result, expected)

    def test_get_max_sims(self):
        query_vec = np.array([1, 0, 1])
        result = get_max_sims(self.df, query_vec, 1)
        expected = [{'title': 'Book 2',
                     'author': 'Author 2',
                     'genres': {'g': 'Non-Fiction'},
                     'summary': 'Summary 2',
                     'pub_date': '2022-01-02',
                     'embedding': [1, 0, 1],
                     'sims': cosine_sim(query_vec, np.array([1, 0, 1]))}]
        self.assertListEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
