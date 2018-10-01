#!/usr/bin/env bash

target_dir=$PWD/demokratikollen/data/dumps
cd docker/dev
docker-compose stop
docker cp $(docker-compose ps -q postgres):/var/lib/postgresql - | gzip > $target_dir/postgres.tar.gz
docker cp $(docker-compose ps -q mongo):/data/db - | gzip > $target_dir/mongodb.tar.gz