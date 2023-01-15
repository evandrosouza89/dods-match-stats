#!/bin/bash

INPUT_FILE='servers.txt'

DMS_HOME=/opt/dods-match-stats
DMS_DB_URL="dods-match-stats-db"
DMS_DB_PORT=3306
DMS_DB_USR="secret"
DMS_DB_PW="secret"
DMS_DB_SCH="dods-match-stats"
DMS_NETWORK="dms-network"
DMS_HTML_OUTPUT="/var/www/dods-match-stats/html"

function getContainerHealth {
  docker inspect --format "{{.State.Health.Status}}" "$1"
}

function waitContainer {
  while STATUS=$(getContainerHealth "$1"); [ "$STATUS" != "healthy" ]; do
    if [ "$STATUS" == "unhealthy" ]; then
      echo "Failed!"
      exit 255
    fi
    printf .
    lf=$'\n'
    sleep 1
  done
  printf '%s' "$lf"
}

if ! docker info > /dev/null 2>&1; then
  echo "This script uses docker, and it isn't running - please start docker and try again!"
  exit 1
fi

if ! [ -f "$INPUT_FILE" ]; then
    echo "This script reads a input file named $INPUT_FILE"" - please create $INPUT_FILE, fill it with one <game server ip>;<desired dods-match-stats port> per line and try again!"
    exit 1
fi

echo "Creating network..."

docker network create "$DMS_NETWORK" >/dev/null 2>&1

echo "Network created!"

echo "Starting database container..."

docker start "$DMS_DB_URL" >/dev/null 2>&1 || \
docker run --name "$DMS_DB_URL" \
          -P \
          -p "$DMS_DB_PORT":"$DMS_DB_PORT" \
          -d \
          -e MYSQL_ROOT_PASSWORD="$DMS_DB_PW" \
          -e MYSQL_USER="$DMS_DB_USR" \
          -e MYSQL_PASSWORD="$DMS_DB_PW" \
          -e MYSQL_DATABASE="$DMS_DB_SCH" \
          --network="$DMS_NETWORK" \
          --health-cmd="mysqladmin ping --silent" \
          mysql:8

waitContainer "$DMS_DB_URL"

echo "Database container started!"

while read -r line; do

  entries=(${line//;/ })

  ip=${entries[0]}
  port=${entries[1]}

  echo "Starting game log parser for game server $ip""..."

  docker start dods-match-stats"$port" >/dev/null 2>&1 || \
  docker run --name dods-match-stats"$port" \
              -d \
               -p "$port":"$port"/udp \
               -e DMS_SV_IP="$ip" \
               -e DMS_PORT="$port" \
               -e DMS_DB_URL="$DMS_DB_URL" \
               -e DMS_DB_PORT="$DMS_DB_PORT" \
               -e DMS_DB_USR="$DMS_DB_USR" \
               -e DMS_DB_PW="$DMS_DB_PW" \
               -e DMS_DB_SCH="$DMS_DB_SCH" \
               --network="$DMS_NETWORK" \
               -v "$DMS_HTML_OUTPUT":"$DMS_HTML_OUTPUT" \
               evandrosouza89/dods-match-stats:latest

  docker exec dods-match-stats"$port" cp "$DMS_HOME"/assets/paper.jpg "$DMS_HTML_OUTPUT"

  sleep 3

  echo "Game log parser started at UDP port $port""!"

done <$INPUT_FILE

echo "dods-match-stats started!"