FROM python:3.4.2
MAINTAINER joharohl <johan@rohlen.net>

COPY ./demokratikollen /usr/src/apps/demokratikollen
WORKDIR /usr/src/apps/demokratikollen
RUN pip install -r requirements.txt -q

ENV PYTHONPATH /usr/src/apps