#!/usr/bin/env bash

set -ex

pip3 install flake8==7.1.1 pylint==3.3.1

ROOT_DIR=$(git rev-parse --show-toplevel)

pylint -E ${ROOT_DIR}/*.py
flake8 ${ROOT_DIR}/*.py
