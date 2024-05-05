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

# Elasticsearch

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
   