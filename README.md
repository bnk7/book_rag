# book_rag

## Current Elasticsearch instructions
```
$ docker network create elastic
$ docker build -t es_test -f es_dockerfile .
$ docker run --name es01 --net elastic -p 9200:9200 -it -m 0.5GB es_test
```
You may need to add `winpty` at the beginning of the `run` command. 
Then, copy and paste the password for the elastic user into a file called es_password.txt in the repository's root folder.

In a separate window, create the Elasticsearch index:
```
$ python elasticsearch_index.py --index_name books
```
Then you can test it with
```
$ python elastic_search.py
```
