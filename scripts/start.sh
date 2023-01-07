#!/bin/bash

DMS_DB_URL="dods-match-stats-db"
DMS_DB_PORT=3306
DMS_DB_USR="secret"
DMS_DB_PW="secret"
DMS_DB_SCH="dods-match-stats"

DMS_NETWORK="dms-network"

docker network create "$DMS_NETWORK"

docker run --name "$DMS_DB_URL" -P -d -e MYSQL_ROOT_PASSWORD="$DMS_DB_PW" -e MYSQL_USER="$DMS_DB_USR" -e MYSQL_PASSWORD="$DMS_DB_PW" -e MYSQL_DATABASE="$DMS_DB_SCH" --network="$DMS_NETWORK" mysql:8

sleep 10

FILE_NAME='servers.txt'

while read -r line; do

  entries=(${line//;/ })

  ip=${entries[0]}
  port=${entries[1]}

  docker run --name dods-match-stats"$port" -d -p "$port" -e DMS_SV_IP="$ip" -e DMS_PORT="$port" -e DMS_DB_URL="$DMS_DB_URL" -e DMS_DB_PORT="$DMS_DB_PORT" -e DMS_DB_USR="$DMS_DB_USR" -e DMS_DB_PW="$DMS_DB_PW" -e DMS_DB_SCH="$DMS_DB_SCH" --network="$DMS_NETWORK" dods-match-stats

  sleep 3

done <$FILE_NAME
