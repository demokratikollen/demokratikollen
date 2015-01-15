FROM python:3.4.2
MAINTAINER joharohl <johan@rohlen.net>

COPY ./demokratikollen/ /usr/src/apps/demokratikollen/
COPY ./gunicorn_config.py /usr/src/apps/demokratikollen/
COPY ./newrelic.ini /etc/newrelic/
WORKDIR /usr/src/apps/demokratikollen
RUN pip install -r requirements.txt -q

ENV PYTHONPATH /usr/src/apps
ENV DATABASE_URL postgresql://demokratikollen@postgres:5432/demokratikollen
ENV DATABASE_RIKSDAGEN_URL postgresql://demokratikollen@postgres:5432/riksdagen
ENV MONGO_DATABASE_URL mongodb://mongo:27017/demokratikollen
ENV NEW_RELIC_CONFIG_FILE /etc/newrelic/newrelic.ini

EXPOSE 8000

CMD newrelic-admin run-command gunicorn -c /usr/src/apps/demokratikollen/gunicorn_config.py demokratikollen.www.gunicorn_production:app