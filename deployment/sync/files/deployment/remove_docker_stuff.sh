docker rm -f postgres_one
docker rm -f postgres_two
docker rm -f mongo_one
docker rm -f mongo_two
docker rm -f webapp_one
docker rm -f webapp_two
docker rm -f bgtasks_one
docker rm -f bgtasks_two
docker rm -f nginx_one
docker rm -f nginx_two

docker rmi demokratikollen/postgres:one
docker rmi demokratikollen/postgres:two
docker rmi demokratikollen/mongo:one
docker rmi demokratikollen/mongo:two
docker rmi demokratikollen/webapp:one
docker rmi demokratikollen/webapp:two
docker rmi demokratikollen/bgtasks:one
docker rmi demokratikollen/bgtasks:two
docker rmi demokratikollen/nginx:one
docker rmi demokratikollen/nginx:two

rm /home/wercker/docker_params