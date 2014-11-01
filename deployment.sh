#!/bin/bash

mkdir -p docker

#copy files
cp -r src/dockerfiles/webapp docker/
cp -r src/dockerfiles/postgres docker/
cp -r src/dockerfiles/mongo docker/

cp -r src/demokratikollen/* docker/webapp/


#Get the postgres image id, if it does not exist, create it
postgres_image_id=`sudo docker images | sed -nr 's/demokratikollen\/postgres\s*latest\s*([a-z0-9]*).*/\1/p'`

if [ -z $postgres_image_id ]; then
    postgres_image_id=`sudo docker build -t demokratikollen/postgres docker/postgres`
fi

#Get the posgres container id, if it does not exist create it
postgres_container_id=`sudo docker ps | sed -nr 's/([a-z0-9]*)\s*demokratikollen\/postgres.*/\1/p'`

if [ -z $postgres_container_id ]; then
    postgres_container_id=`sudo docker run -d --name postgres demokratikollen/postgres`
fi

#Get the webapp image id. Build it if it does not exist
webapp_image_id=`sudo docker images | sed -nr 's/demokratikollen\/webapp\s*latest\s*([a-z0-9]*).*/\1/p'`

if [ -z $webapp_image_id ]; then
	webapp_image_id=`sudo docker build -t demokratikollen/webapp docker/webapp`
	#build environment variables needed by the webapp
	#envs="DATABASE_URL=postgresql://demokratikollen@localhost:"
	#link the webapp to the postgresql database.
	#docker run 
fi

#Get the webapp container id. Start it if it does not exist
webapp_container_id=`sudo docker ps | sed -nr 's/([a-z0-9]*)\s*demokratikollen\/webapp.*/\1/p'`

#if [ -z -f $webapp_container_id ]; then
#    webapp_container_id=`docker run -d --name webapp demokratikollen/webapp`
#fi



#remove files.
rm -rf docker/webapp
rm -rf docker/postgres
rm -rf docker/mongo
