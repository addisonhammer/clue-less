FROM python:alpine

EXPOSE 5000

WORKDIR /client
ADD . /client

RUN python3 -m pip install flask
RUN pip install requests