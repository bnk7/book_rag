from flask import Flask, request, render_template
from llm import get_answer, dict_to_commas, choose_best_book
from utils import convert_date
from alchemy_database import make_book_db, make_book_df, process_query_and_search

app = Flask(__name__)
# instantiate SQLAlchemy database
DATABASE_URL = "sqlite:///books_db.db"
db = make_book_db(DATABASE_URL)
book_df = make_book_df(db)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        query = request.form["query"]
        # retrieve best three books
        docs = process_query_and_search(query, book_df, 3)
        # select top book via llm
        doc = choose_best_book(query, docs)
        # format data for nice printing on frontend
        author = doc["author"] if doc["author"] else "N/A"
        genres = dict_to_commas(doc["genres"]) if doc["genres"] else "N/A"
        if doc["pub_date"]:
            if len(doc["pub_date"]) > 4:
                date = convert_date(doc["pub_date"])
            else:
                date = doc["pub_date"]
        else:
            date = "N/A"
        llm_output = get_answer(query, doc)

        return render_template(
            "results.html",
            query=query,
            generation=llm_output,
            title=doc["title"],
            author=author,
            genres=genres,
            date=date,
            summary=doc["summary"]
        )


if __name__ == "__main__":
    app.run(debug=True, port=8080, host="0.0.0.0")
