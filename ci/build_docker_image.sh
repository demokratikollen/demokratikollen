docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"
docker build -t demokratikollen/web:${TRAVIS_BRANCH} -f docker/prod/web-dockerfile .
docker push demokratikollen/web:${TRAVIS_BRANCH}
