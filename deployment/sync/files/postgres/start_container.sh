#!/bin/bash

#start the containers if they are not running.
files=$(ls /home/wercker/iids/ -l | sed -rn 's/.*(postgres_.+)/\1/gp')
for file in $files ; do
	if ! [ -a /home/wercker/cids/$file ] ; then
		sudo docker run -d --name $file --cidfile /home/wercker/cids/$file demokratikollen/postgres:$file
	fi
done