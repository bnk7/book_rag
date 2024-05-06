import unittest
from llm import get_prompt


class TestGetPrompt(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.question = 'What does the dagger symbolize in Macbeth?'

    def test_system_instruction(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   'pub_date': '1606',
                   'genres': {'0': 'Shakespearean tragedy'},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(self.question, context)[0].content
        expected = """Answer only the question asked; the response should be concise and relevant to the question."""
        self.assertEqual(expected, output)

    def test_all_standard_values(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   'pub_date': '1606',
                   'genres': {'0': 'Shakespearean tragedy'},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(self.question, context)[1].content
        expected = """Context:\nMacbeth was written by William Shakespeare in 1606. It is a work of Shakespearean tragedy. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.\n---\nNow here is the question you need to answer.\nQuestion: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_formatted_date(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   'pub_date': '1606-05-15',
                   'genres': {'0': 'Shakespearean tragedy'},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(self.question, context)[1].content
        expected = """Context:\nMacbeth was written by William Shakespeare in 1606. It is a work of Shakespearean tragedy. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.\n---\nNow here is the question you need to answer.\nQuestion: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_two_genres(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   'pub_date': '1606-05-15',
                   'genres': {'0': 'Shakespearean tragedy', '1': 'Tragedy'},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(self.question, context)[1].content
        expected = """Context:\nMacbeth was written by William Shakespeare in 1606. It is a work of Shakespearean tragedy and Tragedy. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.\n---\nNow here is the question you need to answer.\nQuestion: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_many_genres(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   'pub_date': '1606-05-15',
                   'genres': {'0': 'Shakespearean tragedy', '1': 'Tragedy', '2': 'Theatre', '3': 'Shakespearean Theatre'},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(self.question, context)[1].content
        expected = """Context:\nMacbeth was written by William Shakespeare in 1606. It is a work of Shakespearean tragedy, Tragedy, Theatre, and Shakespearean Theatre. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.\n---\nNow here is the question you need to answer.\nQuestion: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_minimum_info(self):
        context = {'title': 'Macbeth',
                   'author': None,
                   'pub_date': None,
                   'genres': None,
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(self.question, context)[1].content
        expected = """Context:\nHere is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.\n---\nNow here is the question you need to answer.\nQuestion: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_just_author(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   'pub_date': None,
                   'genres': None,
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(self.question, context)[1].content
        expected = """Context:\nMacbeth was written by William Shakespeare. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.\n---\nNow here is the question you need to answer.\nQuestion: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_just_date(self):
        context = {'title': 'Macbeth',
                   'author': None,
                   'pub_date': '1606',
                   'genres': None,
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(self.question, context)[1].content
        expected = """Context:\nMacbeth was written in 1606. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.\n---\nNow here is the question you need to answer.\nQuestion: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_just_genre(self):
        context = {'title': 'Macbeth',
                   'author': None,
                   'pub_date': None,
                   'genres': {'0': 'Shakespearean tragedy'},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(self.question, context)[1].content
        expected = """Context:\nMacbeth is a work of Shakespearean tragedy. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.\n---\nNow here is the question you need to answer.\nQuestion: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_no_author(self):
        context = {'title': 'Macbeth',
                   'author': None,
                   'pub_date': '1606',
                   'genres': {'0': 'Shakespearean tragedy'},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(self.question, context)[1].content
        expected = """Context:\nMacbeth was written in 1606. It is a work of Shakespearean tragedy. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.\n---\nNow here is the question you need to answer.\nQuestion: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_no_date(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   'pub_date': None,
                   'genres': {'0': 'Shakespearean tragedy'},
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(self.question, context)[1].content
        expected = """Context:\nMacbeth was written by William Shakespeare. It is a work of Shakespearean tragedy. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.\n---\nNow here is the question you need to answer.\nQuestion: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)

    def test_no_genre(self):
        context = {'title': 'Macbeth',
                   'author': 'William Shakespeare',
                   'pub_date': '1606',
                   'genres': None,
                   'summary': 'A man tries to avoid his destiny but it comes to him anyways.'
                   }
        output = get_prompt(self.question, context)[1].content
        expected = """Context:\nMacbeth was written by William Shakespeare in 1606. Here is a summary of Macbeth: A man tries to avoid his destiny but it comes to him anyways.\n---\nNow here is the question you need to answer.\nQuestion: What does the dagger symbolize in Macbeth?"""
        self.assertEqual(expected, output)


if __name__ == '__main__':
    unittest.main()
