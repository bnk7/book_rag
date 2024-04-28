FROM docker.elastic.co/elasticsearch/elasticsearch:8.13.2
COPY --chown=elasticsearch:elasticsearch elasticsearch.yml /usr/share/elasticsearch/config/
