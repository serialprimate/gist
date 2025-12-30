#!/usr/bin/env bash

set -euo pipefail

if [[ ${VIRTUAL_ENV+x} ]]
then
    echo "Error: Cannot run while in virtual environment."
    exit 1
fi

if [[ -d .venv ]]
then
    echo "Error: In a project with a virtual environment already."
    exit 1
fi

python3 -m venv --clear .venv

(
    source .venv/bin/activate
    pip install --upgrade pip
    pip install --upgrade pip-tools
    pip-compile --resolver=backtracking --strip-extras --upgrade requirements.in
    pip-compile --resolver=backtracking --strip-extras --upgrade requirements-dev.in
    pip-sync requirements.txt requirements-dev.txt --pip-args '--no-cache-dir --no-deps'

    mkdir dist
)

echo Done
