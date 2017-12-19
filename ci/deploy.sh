#! /bin/bash

ssh_command="ssh -o StrictHostKeyChecking=no -o BatchMode=yes -i ci/deploy_key -l demokratikollen $SERVER_TO_DEPLOY_TO"

$ssh_command rm -rf demokratikollen
$ssh_command git clone --shallow --branch ${TRAVIS_BRANCH} https://github.com/demokratikollen/demokratikollen.git
$ssh_command cd demokratikollen/docker/prod && BRANCH=${TRAVIS_BRANCH} docker-compose up -d