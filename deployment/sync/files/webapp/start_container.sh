#!/bin/bash

#start the containers if they are not running.
files=$(ls /home/wercker/iids/ -l | sed -rn 's/.*(webapp_.+)/\1/gp')
for file in $files ; do
	if ! [ -a /home/wercker/cids/$file ] ; then

		#find out which containers we should link to:
		if [ /home/wercker/cids/postgres_one -nt /home/wercker/cids/postgres_two ]; then
			postgres_name="postgres_one"
		else
			postgres_name="postgres_two"
		fi

		if [ /home/wercker/cids/mongo_one -nt /home/wercker/cids/mongo_two ]; then
			mongo_name="mongo_one"
		else
			mongo_name="mongo_two"
		fi

		sudo docker run -d --name $file --cidfile /home/wercker/cids/$file --link $mongo_name:mongo --link $postgres_name:postgres demokratikollen/webapp:$file
	fi
done