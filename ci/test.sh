#!/usr/bin/env bash

declare TRAVIS_BUILD_DIR

export DATABASE_URL=postgresql://demo:demo@localhost:5432/demokratikollen
export DATABASE_RIKSDAGEN_URL=postgresql://demo:demo@localhost:5432/riksdagen
export MONGO_DATABASE_URL=mongodb://localhost:27017/local
export PYTHONPATH=${TRAVIS_BUILD_DIR:-$PWD}

pushd docker/compose/test
docker-compose down --rmi local
docker-compose up -d
docker ps -a
popd

sleep 60

py.test demokratikollen