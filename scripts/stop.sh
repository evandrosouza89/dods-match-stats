#!/bin/bash

if ! docker info > /dev/null 2>&1; then
  echo "This script uses docker, and it isn't running - please start docker and try again!"
  exit 1
fi

echo "stopping dods-match-stats..."

docker container stop $(docker container ls -q --filter name=dods-match-stats*) > /dev/null 2>&1

echo "dods-match-stats stopped!"