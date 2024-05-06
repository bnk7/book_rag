FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN python -m nltk.downloader punkt
CMD ["python", "main.py"]