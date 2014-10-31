#!/bin/bash

#create the dir structure
mkdir -p docker/app
mkdir -p docker/postgres
mkdir -p docker/mongo

#copy files
cp -r src/dockerfiles/webapp docker
cp -r src/dockerfiles/postgres docker
cp -r src/dockerfiles/mongo docker

cp -r src/demokratikollen/* docker/webapp


#Build the postgres image if it does not exist.
if [ ! -f /home/wercker/docker/imids/postgres ]; then
    docker build -t demokratikollen/postgres docker/postgres> /home/wercker/docker/imids/postgres
fi

#If the container isn't alreay running, start it
if [ ! -f /home/wercker/docker/coids/postgres ]; then
    docker run -d --name postgres demokratikollen/postgres > /home/wercker/docker/coids/postgres
fi

#remove files.
rm -rf docker/webapp
rm -rf docker/postgres
rm -rf docker/mongo
