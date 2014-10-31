#!/bin/bash

#create the dir structure
mkdir docker
mkdir docker/app
mkdir docker/postgres
mkdir docker/mongo

#copy files
cp -r src/dockerfiles/webapp/ docker/app
cp -r src/dockerfiles/postgres/ docker/postgres
cp -r src/dockerfiles/mongo.dockerfile/ docker/mongo

cp -r src/demokratikollen/ docker/app/


#Build the postgres image if it does not exist.
if [-f /docker/imids/postgres]; then
    docker build -t demokratikollen/postgres docker/postgres > /home/wercker/docker/imids
fi

#If the container isn't alreay running, start it
if [-f /docker/coids/postgres]; then
    docker run -d --name postgres demokratikollen/postgres
fi

#remove files.
rm -rf src/dockerfiles/webapp/ docker/app
rm -rf src/dockerfiles/postgres/ docker/postgres
rm -rf src/dockerfiles/mongo.dockerfile/ docker/mongo
