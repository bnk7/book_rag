""" Code used to generate author and date test questions"""

from alchemy_database import make_book_db, make_book_df
import json

if __name__ == '__main__':
    DATABASE_URL = "sqlite:///books_db.db"
    db = make_book_db(DATABASE_URL)
    book_df = make_book_df(db)

    # make questions of the form "When was [Title] written?" with the answer being "[publish date]"
    for _, row in book_df.iterrows():
        if row['pub_date']:
            result = {'id': int(row['id']),
                      'title': row['title'],
                      'author': row['author'],
                      'genres': row['genres'],
                      'summary': row['summary'],
                      'pub_date': row['pub_date']}
            question = "When was " + result['title'] + " written?"
            answer = result['pub_date']
            result['question'] = question
            result['answer'] = answer
            with open('date_test_qs!!.jsonl', 'a') as f:
                json.dump(result, f)
                f.write('\n')

    # make questions of the form "Who is the author of [Title]?" with the answer being "[Author]"
    for _, row in book_df.iterrows():
        if row['author']:
            result = {'id': int(row['id']),
                      'title': row['title'],
                      'author': row['author'],
                      'genres': row['genres'],
                      'summary': row['summary'],
                      'pub_date': row['pub_date']}
            question = "Who is the author of " + result['title'] + "?"
            answer = result['author']
            result['question'] = question
            result['answer'] = answer
            with open('author_test_qs!!.jsonl', 'a') as f:
                json.dump(result, f)
                f.write('\n')
