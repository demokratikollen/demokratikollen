#!/bin/bash

#Check which name we should use
if [ -a /home/wercker/iids/postgres_one ]; then
	name="postgres_two"
else
	name="postgres_one"
fi

#create_a new postgres_image
sudo docker build -q -t demokratikollen/postgres:$name /home/wercker/docker/postgres

#put in an "iid" file
touch /home/wercker/iids/$name