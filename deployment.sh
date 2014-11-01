#!/bin/bash

mkdir -p docker
mkdir -p data

#kill everything for now.
sudo docker rm -f $(sudo docker ps -a -q)
sudo docker rmi demokratikollen/postgres
sudo docker rmi demokratikollen/webapp
sudo docker rmi demokratikollen/nginx

#copy files
cp -r src/dockerfiles/webapp docker/
cp -r src/dockerfiles/postgres docker/
cp -r src/dockerfiles/mongo docker/
cp -r src/dockerfiles/nginx docker/

cp -r src/demokratikollen/* docker/webapp/

#don't go crazy on the downloads
echo "http://data.riksdagen.se/dataset/person/person.sql.zip" > data/urls.txt
echo "http://data.riksdagen.se/dataset/votering/votering-201314.sql.zip" >> data/urls.txt
echo "http://data.riksdagen.se/dataset/dokument/bet-2010-2013.sql.zip" >> data/urls.txt
cp src/demokratikollen/data/create_tables.sql data/

echo "Creating postgres images and containers"
#Get the postgres image id, if it does not exist, create it
postgres_image_id=`sudo docker images | sed -nr 's/demokratikollen\/postgres\s*[a-z0-9]*\s*([a-z0-9]*).*/\1/p'`

if [ -z $postgres_image_id ]; then
    sudo docker build -t demokratikollen/postgres docker/postgres
fi

#Get the posgres container id, if it does not exist create it
postgres_container_id=`sudo docker ps | sed -nr 's/([a-z0-9]*)\s*demokratikollen\/postgres.*/\1/p'`

if [ -z $postgres_container_id ]; then
    sudo docker run -d --name postgres demokratikollen/postgres
fi

echo "Creating webapp images and containers"
#Get the webapp image id. Build it if it does not exist
webapp_image_id=`sudo docker images | sed -nr 's/demokratikollen\/webapp\s*[a-z0-9]*\s*([a-z0-9]*).*/\1/p'`

if [ -z $webapp_image_id ]; then
	sudo docker build -t demokratikollen/webapp docker/webapp

	db_main_env="DATABASE_URL=postgresql://demokratikollen@db:5432/demokratikollen"
	db_riksdagen_env="DATABASE_RIKSDAGEN_URL=postgresql://demokratikollen@db:5432/riksdagen"
	
	#populate the riksdagen database
	sudo docker run --name webapp -e $db_main_env -e $db_riksdagen_env -w /usr/src/apps/demokratikollen --volume /home/wercker/data:/data --link postgres:db demokratikollen/webapp python import_data.py auto /data/urls.txt --wipe
	sudo docker commit webapp demokratikollen/webapp
	sudo docker rm webapp

	#populate the orm
	sudo docker run --name webapp -e $db_main_env -e $db_riksdagen_env -w /usr/src/apps/demokratikollen --link postgres:db demokratikollen/webapp python populate_orm.py
	sudo docker commit webapp demokratikollen/webapp
	sudo docker rm webapp

	#create the final container
	sudo docker create --name webapp -e $db_main_env -e $db_riksdagen_env --link postgres:db demokratikollen/webapp python /usr/src/apps/demokratikollen/www/run.py
	sudo docker commit webapp demokratikollen/webapp
fi

#Get the webapp container id. Start it if it is not already started
webapp_container_id=`sudo docker ps | sed -nr 's/([a-z0-9]*)\s*demokratikollen\/webapp.*/\1/p'`

if [ -z $webapp_container_id ]; then
    sudo docker start webapp
fi

echo "Creating nginx images and containers"
#Create the nginx image if it does not exist
nginx_image_id=`sudo docker images | sed -nr 's/demokratikollen\/nginx\s*[a-z0-9]*\s*([a-z0-9]*).*/\1/p'`

if [ -z $nginx_image_id ]; then
    sudo docker build -t demokratikollen/nginx docker/nginx
fi

#Get the webapp container id. Start it if it is not already started
nginx_container_id=`sudo docker ps | sed -nr 's/([a-z0-9]*)\s*demokratikollen\/nginx.*/\1/p'`

if [ -z $nginx_container_id ]; then
    sudo docker run -d -P --link webapp:webapp demokratikollen/nginx 
fi

#remove files.
rm -rf docker/webapp
rm -rf docker/postgres
rm -rf docker/mongo
