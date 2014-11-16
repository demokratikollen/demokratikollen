#!/bin/bash

#Check if the files to download have changed size remotely
data_file_path="/home/wercker/data/download/"
while read url; do
	local_file=$(echo "$url" | sed -n 's/http:\/\/data\.riksdagen\.se\/.*\///gp')
	local_file="$data_file_path$local_file"
	remote_size=$(curl -Is $url | sed -nr 's/Content-Length: ([0-9]+).*/\1/gp')
	local_size=$(ls -l $local_file | sed -rn 's/.*root root ([0-9]+).*/\1/gp')

	echo "$local_file: Remote size:$remote_size, Local size:$local_size"

	if [ "$remote_size" != "$local_size" ]; then
		echo "File is different. Preparing rebuild."
		exit 1
	fi

done < <(grep '' /home/wercker/docker/bgtasks/demokratikollen/data/urls.txt)