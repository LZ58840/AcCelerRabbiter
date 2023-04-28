#!/bin/bash

set -e
set -a

# https://stackoverflow.com/questions/59895/how-to-get-the-source-directory-of-a-bash-script-from-within-the-script-itself
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source "$SCRIPT_DIR/.env"

set +a

echo "Clearing volumes..."
docker volume rm celeryrabbit_mysql
docker volume rm celeryrabbit_rabbitmq
