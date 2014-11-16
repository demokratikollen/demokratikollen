#!/bin/bash

#Check which running container we should delete. (if both doesn't exist don't kill it)
if [ -a /home/wercker/cids/bgtasks_one ] && [ -a /home/wercker/cids/bgtasks_two ]; then
	if [ /home/wercker/cids/bgtasks_one -ot /home/wercker/cids/bgtasks_two ]; then
		name="bgtasks_one"
	else
		name="bgtasks_two"
	fi

	cid=$(cat /home/wercker/cids/$name)

	#stop and remove the container.
	sudo docker stop $cid
	sudo docker rm $cid
	rm -f /home/wercker/cids/$name

	#remove the image
	sudo docker rmi demokratikollen/bgtasks:$name
	rm /home/wercker/iids/$name
fi