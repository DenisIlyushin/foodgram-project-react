FROM python:3.7-slim

LABEL author='DenisIlyushin'
LABEL version=1.0
LABEL description='Sprint_14 learning docker container'

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD gunicorn foodgram.wsgi:application --bind 0:8000