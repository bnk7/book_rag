FROM docker.elastic.co/elasticsearch/elasticsearch:8.13.2
COPY . .
WORKDIR /app