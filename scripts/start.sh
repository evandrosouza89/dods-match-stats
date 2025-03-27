#!/bin/bash

SERVERS_FILE="servers.txt"
CONFIG_FILE="config_file.config"

DMS_DB_URL="dods-match-stats-db"
DMS_DB_PORT=3306
DMS_DB_USR="secret"
DMS_DB_PW="secret"
DMS_DB_SCHEMA="dods-match-stats"
DMS_NETWORK="dms-network"

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

# Check if the config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Config file $CONFIG_FILE not found!"
  exit 1
fi

# Read the config file and export each key=value pair as an environment variable
while IFS='=' read -r key value; do
  # Skip comments and empty lines
  if [[ "$key" =~ ^#.* ]] || [[ -z "$key" ]]; then
    continue
  fi

  # Export the key-value pair as an environment variable
  export "$key=$value"

done < "$CONFIG_FILE"

# Ensure the output directory exists and has the correct permissions
if [ ! -d "$DMS_OUTPUT_DIR" ]; then
  mkdir -p "$DMS_OUTPUT_DIR"
  chmod 777 "$DMS_OUTPUT_DIR"
fi

if ! docker info > /dev/null 2>&1; then
  echo "This script uses docker, and it isn't running - please start docker and try again!"
  exit 1
fi

if ! [ -f "$SERVERS_FILE" ]; then
    echo "This script reads a input file named $SERVERS_FILE - please create $SERVERS_FILE, fill it with one <game server ip>;<desired dods-match-stats port> per line and try again!"
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
          -e MYSQL_DATABASE="$DMS_DB_SCHEMA" \
          --network="$DMS_NETWORK" \
          --health-cmd="mysqladmin ping --silent" \
          mysql:8

waitContainer "$DMS_DB_URL"

echo "Database container started!"

# Load servers from the server file and create a dods-match-stats container for each entry
while IFS= read -r line; do

  # Skip empty lines
  [[ -z "$line" ]] && continue

  entries=(${line//;/ })

  ip=${entries[0]}
  port=${entries[1]}

  DMS_INSTANCE_NAME="dods-match-stats$port"

  echo "Starting $DMS_INSTANCE_NAME for game server $ip..."

  HOME_DIR="/opt/dods-match-stats"
  OUTPUT_DIR="$HOME_DIR/reports"

  # Either resume existing container or start a new one
  docker start "$DMS_INSTANCE_NAME" >/dev/null 2>&1 || \
  docker run --name "$DMS_INSTANCE_NAME" \
              -d \
               --network="$DMS_NETWORK" \
               -v "$DMS_OUTPUT_DIR":"/opt/dods-match-stats/reports" \
               -e HOME_DIR="$HOME_DIR" \
               -e OUTPUT_DIR="$OUTPUT_DIR" \
               -e DMS_INSTANCE_NAME="$DMS_INSTANCE_NAME" \
               -e DMS_OUTPUT_DIR="$DMS_OUTPUT_DIR" \
               -e DMS_GAME_SERVER_IP="$ip" \
               -e DMS_PORT="$port" \
               -e DMS_DB_URL="$DMS_DB_URL" \
               -e DMS_DB_PORT="$DMS_DB_PORT" \
               -e DMS_DB_USR="$DMS_DB_USR" \
               -e DMS_DB_PW="$DMS_DB_PW" \
               -e DMS_DB_SCHEMA="$DMS_DB_SCHEMA" \
               -e DMS_EXTERNAL_URL="$DMS_EXTERNAL_URL" \
               -e DMS_DISCORD_ENABLED="$DMS_DISCORD_ENABLED" \
               -e DMS_DISCORD_TOKEN="$DMS_DISCORD_TOKEN" \
               -e DMS_DISCORD_CHANNEL_ID="$DMS_DISCORD_CHANNEL_ID" \
               -e DMS_IPB_ENABLED="$DMS_IPB_ENABLED" \
               -e DMS_IPB_API_URL="$DMS_IPB_API_URL" \
               -e DMS_IPB_API_KEY="$DMS_IPB_API_KEY" \
               -e DMS_IPB_FORUM_ID="$DMS_IPB_FORUM_ID" \
               -e DMS_IPB_AUTHOR_ID="$DMS_IPB_AUTHOR_ID" \
               -e DMS_IPB_TOPIC_SUFFIX="$DMS_IPB_TOPIC_SUFFIX" \
               -e DMS_IPB_POST_PREFIX="$DMS_IPB_POST_PREFIX" \
               -e DMS_IPB_LINK_TEXT="$DMS_IPB_LINK_TEXT" \
               evandrosouza89/dods-match-stats:latest

  sleep 3

  echo "Game log parser started at UDP port $port!"

done < "$SERVERS_FILE"

echo "dods-match-stats started!"
