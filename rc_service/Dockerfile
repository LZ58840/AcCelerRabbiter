FROM hdgigante/python-opencv:4.7.0-alpine

RUN apk add gcc musl-dev mariadb-connector-c-dev
ENV PYTHONBUFFERED 1

COPY rc_service rc_service
COPY utils.py utils.py
COPY .env .env

RUN pip install -r rc_service/requirements.txt

ENTRYPOINT celery -A rc_service worker --loglevel=info
