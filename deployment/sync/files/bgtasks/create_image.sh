#!/bin/bash

#Check which name we should use
if [ -a /home/wercker/iids/bgtasks_one ]; then
	name="bgtasks_two"
else
	name="bgtasks_one"
fi

#create_a new postgres_image
sudo docker build -q -t demokratikollen/bgtasks:$name /home/wercker/docker/bgtasks

#put in an "iid" file
touch /home/wercker/iids/$name