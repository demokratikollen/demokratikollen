FROM python:3.4.2
MAINTAINER joharohl <johan@rohlen.net>

COPY . /etc/webapp/

RUN pip install -r /etc/webapp/requirements.txt -q

ENV PYTHONPATH /apps
ENV DATABASE_URL postgresql://demokratikollen@postgres:5432/demokratikollen
ENV DATABASE_RIKSDAGEN_URL postgresql://demokratikollen@postgres:5432/riksdagen
ENV MONGO_DATABASE_URL mongodb://mongo:27017/demokratikollen
ENV NEW_RELIC_CONFIG_FILE /etc/webapp/newrelic.ini

EXPOSE 8000

VOLUME /apps
VOLUME /data

CMD newrelic-admin run-program gunicorn -c /etc/webapp/gunicorn_config.py demokratikollen.www.gunicorn_production:app