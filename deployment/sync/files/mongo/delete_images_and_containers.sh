#!/bin/bash

#Check which running container we should delete. (if both doesn't exist don't kill it)
if [ -a /home/wercker/cids/mongo_one ] && [ -a /home/wercker/cids/mongo_two ]; then
	if [ /home/wercker/cids/mongo_one -ot /home/wercker/cids/mongo_two ]; then
		name="mongo_one"
	else
		name="mongo_two"
	fi

	cid=$(cat /home/wercker/cids/$name)

	#stop and remove the container.
	sudo docker stop $cid
	sudo docker rm $cid
	rm -f /home/wercker/cids/$name

	#remove the image
	sudo docker rmi demokratikollen/mongo:$name
	rm /home/wercker/iids/$name
fi