FROM python:3.10-slim-buster

RUN apt-get update
RUN apt-get install -y gcc musl-dev libmariadb3 libmariadb-dev

COPY rc_client rc_client
COPY utils.py utils.py
COPY .env .env

RUN pip install -r rc_client/requirements.txt

ENTRYPOINT python -u -m rc_client
