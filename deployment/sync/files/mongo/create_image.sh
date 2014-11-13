#!/bin/bash

#Check which name we should use
if [ -a /home/wercker/cids/mongo_one ]; then
	name="mongo_two"
else
	name="mongo_one"
fi

#create_a new postgres_image
sudo docker build -q -t demokratikollen/mongo:$name /home/wercker/docker/mongo

#put in an "iid" file
touch /home/wercker/iids/$name