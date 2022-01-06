#!/usr/bin/env bash

set -ex

pip3 install flake8==4.0.1 pylint==2.12.2

ROOT_DIR=$(git rev-parse --show-toplevel)

pylint -E ${ROOT_DIR}/*.py
flake8 ${ROOT_DIR}/*.py
