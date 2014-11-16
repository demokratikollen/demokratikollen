#!/bin/bash

#Check which name we should use
if [ -a /home/wercker/iids/webapp_one ]; then
	name="webapp_two"
else
	name="webapp_one"
fi

#create_a new webapp_image
sudo docker build -q -t demokratikollen/webapp:$name /home/wercker/docker/webapp

#put in an "iid" file
touch /home/wercker/iids/$name