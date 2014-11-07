#!/bin/bash

#first time we run create folders
mkdir -p docker
mkdir -p data

echo "copying new source"
#copy files
cp -r src/dockerfiles/webapp docker/
cp -r src/demokratikollen/* docker/webapp/

cp -r src/dockerfiles/mongo docker/

cp -r src/dockerfiles/postgres docker/

cp -r src/dockerfiles/nginx docker/
cp -r src/demokratikollen/www/app/static docker/nginx/

#copy files for import_data
cp src/demokratikollen/data/create_tables.sql data/
cp src/dockerfiles/webapp/urls.txt data/

#Check if the files to download have changed size remotely
echo "Checking if remote files has changed..."
remote_changed=""
while read url; do
	local_file=$(echo "$url" | sed -n 's/http:\/\/data\.riksdagen\.se\/.*\///gp')
	local_file="data/download/$local_file"
	remote_size=$(curl -Is $url | sed -nr 's/Content-Length: ([0-9]+).*/\1/gp')
	local_size=$(ls -l $local_file | sed -rn 's/.*root root ([0-9]+).*/\1/gp')

    echo "File: $local_file, $remote_size:$local_size"

	if [ "$remote_size" != "$local_size" ]; then
		echo "File is different. Preparing rebuild."
		remote_changed="true"
	fi

done < <(grep '' data/urls.txt)

echo "Checking if src has changed..."
#Check if any of the app changed that requires a rebuild of the databases.
db_structure_diff=$(diff src/demokratikollen/core/db_structure.py old_src/demokratikollen/core/db_structure.py)
setup_diff=$(diff src/dockerfiles/webapp/setup old_src/dockerfiles/webapp/setup)
envs_diff=$(diff src/dockerfiles/webapp/envs old_src/dockerfiles/webapp/envs)
deamon_diff=$(diff src/dockerfiles/webapp/deamon old_src/dockerfiles/webapp/deamon)
urls_diff=$(diff src/dockerfiles/webapp/urls.txt old_src/dockerfiles/webapp/urls.txt)

rebuild_webapp_container="$setup_diff$envs_diff$deamon_diff"
rebuild_riksdagen="$remote_changed$urls_diff"
rebuild_orm="$db_structure_diff$rebuild_riksdagen"

echo "Creating postgres images and containers"
#Get the postgres image id, if it does not exist, create it
postgres_image_id=$(sudo docker images | sed -nr 's/demokratikollen\/postgres.+latest.+([a-z0-9]{12}).*/\1/gp')

if [ -z $postgres_image_id ]; then
    sudo docker build -t demokratikollen/postgres docker/postgres
fi

#Get the postgres container id, if it does not exist create it
postgres_container_id=$(sudo docker ps | sed -nr 's/([0-9a-z]{12}).+postgres/\1/gp')

if [ -z $postgres_container_id ]; then
    sudo docker run -d --name postgres demokratikollen/postgres
fi

echo "Creating mongo images and containers"

mongo_image_id=$(sudo docker images | sed -nr 's/demokratikollen\/mongo.+latest.+([a-z0-9]{12}).*/\1/gp')

if [ -z $mongo_image_id ]; then
	sudo docker build -t demokratikollen/mongo docker/mongo
fi

mongo_container_id=$(sudo docker ps | sed -nr 's/([0-9a-z]{12}).+mongo/\1/gp')

if [ -z $mongo_container_id ]; then
    sudo docker run -d --name mongo demokratikollen/mongo
fi

echo "Creating webapp images and containers"
#Get the webapp image id. Build it if it does not exist
webapp_image_id=$(sudo docker images | sed -nr 's/demokratikollen\/webapp.+latest.+([a-z0-9]{12}).*/\1/gp')

if [ -z $webapp_image_id ]; then
	sudo docker build -t demokratikollen/webapp docker/webapp

	while read cmd; do
		sudo docker $cmd
	done < <(grep '' docker/webapp/setup) 

	#create the final container
	deamon=$(cat docker/webapp/deamon)
	sudo docker $deamon
fi

#Get the webapp container id. Start it if it is not already started
webapp_container_id=$(sudo docker ps | sed -nr 's/([0-9a-z]{12}).+webapp/\1/gp')

if [ -z $webapp_container_id ]; then
    sudo docker start webapp
else #Check if we need to rebuild something.
	if [ -n $rebuild_riksdagen ]; then
		sudo docker exec $webapp_container_id python import_data.py auto /data/urls.txt /data --wipe
	fi
	if [ -n $rebuild_orm ]; then
		sudo docker exec $webapp_container_id python populate_orm.py
		sudo docker exec $webapp_container_id python compute_party_votes.py
	fi
fi

echo "Creating nginx images and containers"
#Create the nginx image if it does not exist
nginx_image_id=$(sudo docker images | sed -nr 's/demokratikollen\/nginx.+latest.+([a-z0-9]{12}).*/\1/gp')

if [ -z $nginx_image_id ]; then
    sudo docker build -t demokratikollen/nginx docker/nginx
fi

#Get the webapp container id. Start it if it is not already started
nginx_container_id=$(sudo docker ps | sed -nr 's/([0-9a-z]{12}).+nginx/\1/gp')

if [ -z $nginx_container_id ]; then
    sudo docker run -d -p 80:80 --name nginx --link webapp:webapp demokratikollen/nginx 
fi

#remove old source files
rm -rf old_src
#copy cur to old
cp -r src old_src

#remove files.
rm -rf docker/webapp
rm -rf docker/postgres
rm -rf docker/mongo
rm -rf docker/nginx