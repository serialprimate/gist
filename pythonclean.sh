#!/usr/bin/env bash

set -euo pipefail

if [[ ${VIRTUAL_ENV+x} ]]
then
    echo "Cannot run while in virtual environment."
    exit 1
fi

if [[ ! -d .venv ]]
then
    echo "Not in a project with a virtual environment."
    exit 1
fi

rm -rf .venv
rm -rf build dist
rm -rf .mypy_cache
find ./src -type d -name '__pycache__' -exec rm -rf {} +
find ./src -type f -name '*.py[co]' -delete
rm -rf .pytest_cache .coverage

echo done
