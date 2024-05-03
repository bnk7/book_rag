FROM docker.elastic.co/elasticsearch/elasticsearch:8.13.2
WORKDIR /app
COPY . .
USER root
RUN apt-get update && apt-get install -y python3-pip
RUN pip install -r requirements.txt
RUN python elasticsearch_index.py
CMD ["python", "main.py"]