#!/usr/bin/env bash -e

declare SERVER_TO_DEPLOY_TO
declare TRAVIS_COMMIT

ENVIRONMENT=${1:-staging}

source ci/environment.sh

ssh_command="ssh -o StrictHostKeyChecking=no -o BatchMode=yes -i ci/deploy_key -l demokratikollen $SERVER_TO_DEPLOY_TO"

${ssh_command} mkdir -p ${ENVIRONMENT}
${ssh_command} rm -rf ${ENVIRONMENT}/demokratikollen
${ssh_command} cd ${ENVIRONMENT} && git clone https://github.com/demokratikollen/demokratikollen.git
${ssh_command} cd ${ENVIRONMENT}/demokratikollen/docker/compose/${ENVIRONMENT} && postgres_md5=${POSTGRES_DATA_HASH} mongodb_md5=${MONGO_DATA_HASH} git_sha=${TRAVIS_COMMIT} docker-compose up -d