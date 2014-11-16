#!/bin/bash

#Check which running container we should delete. (if both doesn't exist assume first run and do nothing.)
if [ -a /home/wercker/cids/webapp_one ] && [ -a /home/wercker/cids/webapp_two ]; then
	if [ /home/wercker/cids/webapp_one -ot /home/wercker/cids/webapp_two ]; then
		name="webapp_one"
	else
		name="webapp_two"
	fi

	cid=$(cat /home/wercker/cids/$name)

	#stop and remove the container.
	sudo docker stop $cid
	sudo docker rm $cid
	rm -f /home/wercker/cids/$name

	#remove the image
	sudo docker rmi demokratikollen/webapp:$name
	rm /home/wercker/iids/$name
fi