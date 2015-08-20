FROM python:2.7

WORKDIR /app
COPY . /app

RUN pip install --upgrade --no-cache-dir -r requirements.txt
