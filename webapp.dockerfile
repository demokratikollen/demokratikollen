
MAINTAINER joharohl

FROM python:3.4.2-onbuild

COPY demokratikollen /app/demokratikollen

RUN pip install -r /app/demokratikollen/requirements.txt

ENV PYTHONPATH=/app
