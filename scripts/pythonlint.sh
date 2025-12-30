#!/usr/bin/env bash

set -euo pipefail

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "Error: Must run in a virtual environment."
  exit 1
fi

echo "Checking import sorting with isort ..."
isort --check-only --diff src/ tests/

echo "Running mypy type checks ..."
mypy src/ tests/

echo "Running pylint lint checks ..."
pylint src/gist tests/

echo Done
