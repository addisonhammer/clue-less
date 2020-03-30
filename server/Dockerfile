FROM python:alpine

WORKDIR /server
ADD . /server

EXPOSE 5000

RUN pip install attrs
RUN pip install flask

# Full install of PostgreSQL python module
RUN apk update
RUN apk add postgresql-dev gcc musl-dev
RUN pip install psycopg2
