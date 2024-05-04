import unittest
from llm import get_prompt

question = "What does the dagger symbolize in Macbeth?"


class TestGetPrompt(unittest.TestCase):
    def test_normal_all_values(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   "pub_date": "1606",
                   "genres": {0: "Shakespearean tragedy"},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(question, context)[1].content
        expected = """Context:
Macbeth was written by William Shakespeare in 1606. It is a work of Shakespearean tragedy. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.
---
Now here is the question you need to answer. 
Question: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_date_format(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   "pub_date": "1606-05-15",
                   "genres": {0: "Shakespearean tragedy"},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(question, context)[1].content
        expected = """Context:
Macbeth was written by William Shakespeare in 1606. It is a work of Shakespearean tragedy. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.
---
Now here is the question you need to answer. 
Question: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_two_genres(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   "pub_date": "1606-05-15",
                   "genres": {0: "Shakespearean tragedy", 1: "Tragedy"},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(question, context)[1].content
        expected = """Context:
Macbeth was written by William Shakespeare in 1606. It is a work of Shakespearean tragedy and Tragedy. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.
---
Now here is the question you need to answer. 
Question: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_many_genres(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   "pub_date": "1606-05-15",
                   "genres": {0: "Shakespearean tragedy", 1: "Tragedy", 2: "Theatre", 3: "Shakespearean Theatre"},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(question, context)[1].content
        expected = """Context:
Macbeth was written by William Shakespeare in 1606. It is a work of Shakespearean tragedy, Tragedy, Theatre and Shakespearean Theatre. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.
---
Now here is the question you need to answer. 
Question: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_base_info(self):
        context = {'title': 'Macbeth',
                   'author': None,
                   'pub_date': None,
                   'genres': None,
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(question, context)[1].content
        expected = """Context:
Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.
---
Now here is the question you need to answer. 
Question: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_just_author(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   'pub_date': None,
                   'genres': None,
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(question, context)[1].content
        expected = """Context:
Macbeth was written by William Shakespeare. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.
---
Now here is the question you need to answer. 
Question: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_just_date(self):
        context = {'title': 'Macbeth',
                   'author': None,
                   'pub_date': "1606",
                   'genres': None,
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(question, context)[1].content
        expected = """Context:
Macbeth was written in 1606. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.
---
Now here is the question you need to answer. 
Question: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_just_genre(self):
        context = {'title': 'Macbeth',
                   'author': None,
                   'pub_date': None,
                   'genres': {0: "Shakespearean tragedy"},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(question, context)[1].content
        expected = """Context:
Macbeth is a work of Shakespearean tragedy. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.
---
Now here is the question you need to answer. 
Question: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_no_author(self):
        context = {'title': 'Macbeth',
                   'author': None,
                   'pub_date': "1606",
                   'genres': {0: "Shakespearean tragedy"},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(question, context)[1].content
        expected = """Context:
Macbeth was written in 1606. It is a work of Shakespearean tragedy. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.
---
Now here is the question you need to answer. 
Question: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_no_date(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   'pub_date': None,
                   'genres': {0: "Shakespearean tragedy"},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(question, context)[1].content
        expected = """Context:
Macbeth was written by William Shakespeare. It is a work of Shakespearean tragedy. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.
---
Now here is the question you need to answer. 
Question: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_no_genre(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   'pub_date': "1606",
                   'genres': None,
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(question, context)[1].content
        expected = """Context:
Macbeth was written by William Shakespeare in 1606. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.
---
Now here is the question you need to answer. 
Question: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)


if __name__ == '__main__':
    unittest.main()
