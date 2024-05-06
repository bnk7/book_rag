# Book RAG
Gabby Masini, Leora Baumgarten, Annika Sparrell, and Brynna Kilcline

May 2024

## Runtime instructions

1. **TODO**: How to get Mistral API key. Copy your key into a file called llm_secret.py in the repository's root directory 
with the format:
    ```
    key = "YOUR-API-KEY"
    ```
2. Build and run the application:
    ```
    $ docker build -t flask_app .
    $ docker run --name flask -dp 8080:8080 flask_app
    ```
3. Navigate to [http://127.0.0.1:8080](http://127.0.0.1:8080) in your browser.

## Testing instructions

To evaluate the system's performance, run:
```
$ docker exec -i flask python evaluate.py
```
To run unit tests, run:
```
$ docker exec -i flask bash run_unit_tests.sh
```

## Elasticsearch

The application uses SQLAlchemy as the database because it integrates smoothly with the tech stack.
However, we did experiment with Elasticsearch, and you can test it out separately.
Here are the steps for running it:
1. Install the required Python packages.
2. In the terminal, run:
   ```
   $ docker network create elastic
   $ docker build -t es -f es_dockerfile .
   $ docker run --name es01 --net elastic -p 9200:9200 -it -m 0.5GB es
   ```
   You may need to add `winpty` at the beginning of the `run` command. 
3. Copy and paste the password for the elastic user into a file called es_password.txt in the repository's root folder.
4. In a separate terminal window, create the Elasticsearch index:
     ```
     $ python elasticsearch_index.py
     ```
5. You may now input your query:
   ```
   $ python elastic_search.py --query <YOUR-QUERY>
   ```

You can also run the unit test to see that its output matches the SQLAlchemy output:
```
$ python test_es.py
```
## File structure
* `static/` - Contains images and styles for the frontend
    * `css/` - Contains CSS file
        * `styles.css` - Project stylesheet 
    * `favicon.ico`
    * `github.png`
* `templates/` - Contains HTML files
    * `index.html` - Start page of site
    * `results.html` - Template for query response page
* `test_data/` - Data files for evaluating scripts
    * `author_test_qs.jsonl`
    * `date_test_qs.jsonl`
    * `test_questions.jsonl`
* `.gitignore` - Gitignore (usual extraneous files plus API key files)
* `alchemy_database.py` - Code for filling and querying the SQLAlchemy database
* `alchemy_tests.py` - Unittests for alchemy database
* `books_db.db` - SQLAlchemy database
* `create_database.py` - Creates the SQLAlchemy database, does not need to be rerun after database exists in project
* `dockerfile` - The Dockerfile to containerize the project
* `elastic_search.py` - Code to query the database via elasticsearch
* `elasticsearch_index.py` - Creates the Elasticsearch index, does not need to be rerun after database exists in project
* `elasticsearch_tests.py` - Unittests for the elasticsearch functionality
* `es_dockerfile` - Specialized Dockerfile required to run Elasticsearch scripts
* `es_password.txt` - Required to be created locally by the user, contains the Elasticsearch password generated with the above instructions
* `evaluate.py` - Runs evaluation scripts on the quality of the answers output by the LLM.
* `evaluation_tests.py` - Unittests for the evaluation scripts
* `generate_test_qs.py` - Creates test data as found in `test_data/`
* `llm.py` - Code to query the Mistral API to obtain LLM responses
* `llm_secret.py` - Required to be created locally by the user, contains a Mistral API key stored in `key`
* `llm_tests.py` - Unittests for the LLM prompting code
* `main.py` - Flask frontend code
* `README.md` - You are here :)
* `requirements.txt` - Project dependencies
* `run_unit_tests.sh` - Runs all unittests in the project
* `utils.py` - Contains short utility functions which are used by multiple other files