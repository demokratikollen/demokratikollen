#!/usr/bin/env bash

POSTGRES_DATA_HASH=$(md5sum demokratikollen/data/dumps/postgres.tar.gz | cut -f1 -d' ')
MONGO_DATA_HASH=$(md5sum demokratikollen/data/dumps/mongodb.tar.gz | cut -f1 -d' ')

docker build -t demokratikollen/postgres:${POSTGRES_DATA_HASH} -f docker/prod/postgres-dockerfile .
docker build -t demokratikollen/mongodb:${MONGO_DATA_HASH} -f docker/prod/mongodb-dockerfile .

docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"

docker push demokratikollen/postgres:${POSTGRES_DATA_HASH}
docker push demokratikollen/mongodb:${MONGO_DATA_HASH}