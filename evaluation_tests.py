import unittest
import warnings
from evaluate import evaluate_contexts, evaluate_answers


class TestEvaluateContext(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.true_context = [{'title': 'Macbeth',
                              'author': 'William Shakespeare',
                              'pub_date': '1606',
                              'genres': {'0': 'Shakespearean tragedy'},
                              'summary': 'A man tries to avoid his destiny but it comes to him anyways.'}]

    def test_correct_context(self):
        predicted_context = [{'title': 'Macbeth',
                             'author': 'William Shakespeare',
                              'pub_date': '1606',
                              'genres': {'0': 'Shakespearean tragedy'},
                              'summary': 'A man tries to avoid his destiny but it comes to him anyways.'}]
        score = evaluate_contexts(self.true_context, predicted_context)
        self.assertEqual(1, score)

    def test_incorrect_title(self):
        predicted_context = [{'title': 'Hamlet',
                             'author': 'William Shakespeare',
                              'pub_date': '1606',
                              'genres': {'0': 'Shakespearean tragedy'},
                              'summary': 'A man tries to avoid his destiny but it comes to him anyways.'}]
        score = evaluate_contexts(self.true_context, predicted_context)
        self.assertEqual(0.55, score)

    def test_incorrect_author(self):
        predicted_context = [{'title': 'Macbeth',
                             'author': 'Jane Austen',
                              'pub_date': '1606',
                              'genres': {'0': 'Shakespearean tragedy'},
                              'summary': 'A man tries to avoid his destiny but it comes to him anyways.'}]
        score = evaluate_contexts(self.true_context, predicted_context)
        self.assertEqual(0.75, score)

    def test_incorrect_date(self):
        predicted_context = [{'title': 'Macbeth',
                             'author': 'William Shakespeare',
                              'pub_date': '1780',
                              'genres': {'0': 'Shakespearean tragedy'},
                              'summary': 'A man tries to avoid his destiny but it comes to him anyways.'}]
        score = evaluate_contexts(self.true_context, predicted_context)
        self.assertEqual(1, score)

    def test_incorrect_genres(self):
        predicted_context = [{'title': 'Macbeth',
                             'author': 'William Shakespeare',
                              'pub_date': '1606',
                              'genres': {'1': 'Tragedy'},
                              'summary': 'A man tries to avoid his destiny but it comes to him anyways.'}]
        score = evaluate_contexts(self.true_context, predicted_context)
        self.assertEqual(1, score)

    def test_partial_summary(self):
        predicted_context = [{'title': 'Macbeth',
                             'author': 'William Shakespeare',
                              'pub_date': '1606',
                              'genres': {'0': 'Shakespearean tragedy'},
                              'summary': 'A man tries and fails to avoid his fate.'}]
        score = evaluate_contexts(self.true_context, predicted_context)
        self.assertEqual(0.82, score)

    def test_incorrect_summary(self):
        predicted_context = [{'title': 'Macbeth',
                             'author': 'William Shakespeare',
                              'pub_date': '1606',
                              'genres': {'0': 'Shakespearean tragedy'},
                              'summary': 'Macbeth charts the bloody rise to power and tragic downfall of a warrior.'}]
        score = evaluate_contexts(self.true_context, predicted_context)
        self.assertEqual(0.7, score)

    def test_incorrect_title_and_author(self):
        predicted_context = [{'title': 'Hamlet',
                             'author': 'Jane Austen',
                              'pub_date': '1780',
                              'genres': {'1': 'Tragedy'},
                              'summary': 'A man tries to avoid his destiny but it comes to him anyways.'}]
        score = evaluate_contexts(self.true_context, predicted_context)
        self.assertEqual(0.3, score)

    def test_incorrect_author_and_summary(self):
        predicted_context = [{'title': 'Macbeth',
                             'author': 'Jane Austen',
                              'pub_date': '1780',
                              'genres': {'1': 'Tragedy'},
                              'summary': 'Macbeth charts the bloody rise to power and tragic downfall of a warrior.'}]
        score = evaluate_contexts(self.true_context, predicted_context)
        self.assertEqual(0.45, score)

    def test_incorrect_title_and_summary(self):
        predicted_context = [{'title': 'Hamlet',
                             'author': 'William Shakespeare',
                              'pub_date': '1780',
                              'genres': {'1': 'Tragedy'},
                              'summary': 'Macbeth charts the bloody rise to power and tragic downfall of a warrior.'}]
        score = evaluate_contexts(self.true_context, predicted_context)
        self.assertEqual(0.25, score)


class TestEvaluateAnswer(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        warnings.simplefilter('ignore')
        self.query = ["What does the dagger represent in Macbeth?"]
        self.true_answer = [
            "The dagger appears throughout the play, in reality and hallucinations, to symbolize Macbeth's violent choice and ambition."]

    def test_correct_answer(self):
        predicted_answer = [
            "The dagger appears throughout the play, in reality and hallucinations, to symbolize Macbeth's violent choice and ambition."]
        score = evaluate_answers(
            self.query, self.true_answer, predicted_answer)
        self.assertEqual(1, score)

    def test_similarity_range(self):
        very_similar_answer = [
            "The dagger shows up throughout the play, in reality and hallucinations, to represent Macbeth's violent decisions and ambition."]
        very_similar_score = evaluate_answers(
            self.query, self.true_answer, very_similar_answer)
        slightly_similar_answer = [
            "The dagger, real and imagined, symbolizes Macbeth's brutal inclinations."]
        slightly_similar_score = evaluate_answers(
            self.query, self.true_answer, slightly_similar_answer)
        different_answer = [
            "The dagger is a weapon that Macbeth uses to kill intruders."]
        different_score = evaluate_answers(
            self.query, self.true_answer, different_answer)
        self.assertGreater(very_similar_score, slightly_similar_score)
        self.assertGreater(slightly_similar_score, different_score)


if __name__ == '__main__':
    unittest.main()
