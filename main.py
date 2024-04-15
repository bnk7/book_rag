from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        query = request.form["query"]
        output = "The book you are asking about is The Lord of the Rings by J.R.R. Tolkien."
        title = "The Lord of the Rings"
        author = "J.R.R. Tolkien"
        date = "1954 (England), 1955 (America)"
        summary = "When one hobbit inherits a magical ring, he never would have imagined that it would lead him on such a perilous quest. Joining three other hobbits, two Men, an Elf, a dwarf, and a wizard, he sets out to destroy the very thing his uncle found so many years before."
        return render_template("results.html", generation=output, title=title, author=author, date=date, summary=summary)


if __name__ == "__main__":
    app.run(debug=True, port=8080)