#!/usr/bin/env bash
# Executes the unit tests: note that this script is designed to be run with Pipenv from 'lambda/' directory:
# pipenv run ./tests/run-unit-tests.sh
set -eu

export PYTHONPATH=src/
coverage run --module pytest --verbose tests/unit && coverage report --show-missing --fail-under=80
