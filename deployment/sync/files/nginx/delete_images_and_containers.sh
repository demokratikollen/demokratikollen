#!/bin/bash

#Check which running container we should delete. (if both doesn't exist don't kill it)
if [ -a /home/wercker/cids/nginx_one ] && [ -a /home/wercker/cids/nginx_two ]; then
	if [ /home/wercker/cids/nginx_one -ot /home/wercker/cids/nginx_two ]; then
		name="nginx_one"
	else
		name="nginx_two"
	fi

	cid=$(cat /home/wercker/cids/$name)

	#stop and remove the container.
	sudo docker stop $cid
	sudo docker rm $cid
	rm -f /home/wercker/cids/$name

	#remove the image
	sudo docker rmi demokratikollen/nginx:$name
	rm /home/wercker/iids/$name
fi