FROM python:3.9.6-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev linux-headers



WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/