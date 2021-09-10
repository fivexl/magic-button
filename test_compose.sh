#!/usr/bin/env bash

export BUILD_JOB_NAME=local-test
export BUILD_JOB_URL=http://whatever.com
export CURRENT_GIT_COMMIT=$(git rev-parse HEAD)
export REPOSITORY_NAME=$(basename $(git rev-parse --show-toplevel))
export REPOSITORY_URL=https://github.com/fivexl/magic-button
export BRANCHES_TO_PROMOTE=test
export TIMEOUT_MINUTES=10
export TIMEZONE=$(cat /etc/timezone)
export PRODUCTION_BRANCH=release
export SLACK_CHANNEL_NAME=magic-button-test

docker-compose up -d --build