from flask import Flask, request, render_template
from llm import get_answer, dict_to_commas, convert_date, choose_best_book
from alchemy_database import make_book_db, make_book_df, process_query_and_search

app = Flask(__name__)
DATABASE_URL = "sqlite:///books_db.db"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        query = request.form["query"]

        db = make_book_db(DATABASE_URL)
        book_df = make_book_df(db)
        docs = process_query_and_search(query, book_df, 3)
        doc = choose_best_book(query, docs)
        author = doc["author"] if doc["author"] is not None else "N/A"
        genres = dict_to_commas(doc["genres"]) if doc["genres"] is not None else "N/A"
        if doc["pub_date"] is not None:
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
