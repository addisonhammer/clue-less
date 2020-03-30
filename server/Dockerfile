FROM python:alpine

EXPOSE 5000

WORKDIR /
ADD ./core /core
ADD ./server /server

ENV PYTHONPATH="$PYTHONPATH:/core"

RUN pip install attrs
RUN pip install flask
RUN pip install networkx

# Full install of PostgreSQL python module
RUN apk update
RUN apk add postgresql-dev gcc musl-dev
RUN pip install psycopg2
