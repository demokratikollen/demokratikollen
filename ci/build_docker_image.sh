docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"
docker build -t demokratikollen/web:${TRAVIS_COMMIT} -f docker/web-prod/Dockerfile .
docker push demokratikollen/web:${TRAVIS_COMMIT}
