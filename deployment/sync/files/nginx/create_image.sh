#!/bin/bash

#Check which name we should use
if [ -a /home/wercker/cids/nginx_one ]; then
	name="nginx_two"
else
	name="nginx_one"
fi

#create_a new postgres_image
sudo docker build -q -t demokratikollen/nginx:$name /home/wercker/docker/nginx

#put in an "iid" file
touch /home/wercker/iids/$name