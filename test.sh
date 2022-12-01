#!/usr/bin/env bash

source ./set_test_env_vars.sh

docker-compose up -d --build
docker-compose logs -f
cat magic-button/reports/report.json | jq