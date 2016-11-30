FROM python:2.7

WORKDIR /app
COPY . /app

RUN pip install --upgrade --no-cache-dir -r requirements.txt

ENV PYTHONPATH=.

CMD ["python", "scripts/manage.py", "runserver", "-t 0.0.0.0", "-p 5000"]
