#!/usr/bin/env bash

source environment.sh

docker build -t demokratikollen/postgres:${POSTGRES_DATA_HASH} -f docker/postgres .
docker build -t demokratikollen/mongodb:${MONGO_DATA_HASH} -f docker/mongodb .

docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"

docker push demokratikollen/postgres:${POSTGRES_DATA_HASH}
docker push demokratikollen/mongodb:${MONGO_DATA_HASH}