#!/usr/bin/python3

import glob
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from src import logger, formatter
from src.database_helper import DatabaseHelper
from src.discord_writer import DiscordWriter
from src.event_processor import EventProcessor
from src.event_reader import EventReader
from src.half_processor import HalfProcessor
from src.html_writer import HtmlWriter
from src.match_state_processor import MatchStateProcessor
from src.match_stats_processor import MatchStatsProcessor
from src.match_writer import MatchWriter
from src.remote_log_listener import RemoteLogListener
from src.topic_writer import TopicWriter


def __init(database_helper, instance_name, output_dir):
    topic_writer = TopicWriter()
    discord_writer = DiscordWriter()
    html_writer = HtmlWriter(output_dir)
    half_processor = HalfProcessor(database_helper, html_writer, topic_writer, discord_writer)
    match_writer = MatchWriter(database_helper, half_processor, instance_name)
    match_stats_processor = MatchStatsProcessor(match_writer)
    match_state_processor = MatchStateProcessor(match_stats_processor)

    return EventProcessor(match_state_processor)


def __read_from_logs_folder(database_helper, instance_name, input_dir, output_dir):
    file_path_list = glob.glob(input_dir)
    file_path_list.sort()

    for file_path in file_path_list:
        f = open(file_path, "r", encoding="utf-8", errors='replace')
        event_processor = __init(database_helper, instance_name, output_dir)
        event_reader = EventReader(f, event_processor)
        event_reader.read()


def __read_from_remote_log_listener(database_helper, instance_name, trusted_ip_address, port, output_dir):
    log_listener = RemoteLogListener(trusted_ip_address, port)
    log_listener.start()
    event_processor = __init(database_helper, instance_name, output_dir)
    event_reader = EventReader(log_listener, event_processor)
    event_reader.read()


def main():
    instance_name = os.getenv("DMS_INSTANCE_NAME")
    output_dir = os.getenv("OUTPUT_DIR")
    trusted_ip_address = os.getenv("DMS_GAME_SERVER_IP")
    port = int(os.getenv("DMS_PORT"))
    input_dir = os.getenv("DMS_INPUT_DIR")
    db_url = os.getenv("DMS_DB_URL")
    db_port = int(os.getenv("DMS_DB_PORT"))
    db_usr = os.getenv("DMS_DB_USR")
    db_pw = os.getenv("DMS_DB_PW")
    db_schema = os.getenv("DMS_DB_SCHEMA")

    if instance_name is None or instance_name.strip() == "":
        print("Instance name must be provided!")
        sys.exit(2)

    if output_dir is None or output_dir.strip() == "":
        print("Output directory must be provided!")
        sys.exit(2)

    if trusted_ip_address is None or trusted_ip_address.strip() == "":
        print("Game server IP must be provided!")
        sys.exit(2)

    if port is None or int(port) < 1 or int(port) > 65535:
        print("A valid UDP port number must be provided!")
        sys.exit(2)

    if db_url is None or db_url.strip() == "":
        print("Database URL must be provided!")
        sys.exit(2)

    if db_port is None or int(db_port) < 1 or int(db_port) > 65535:
        print("A valid MySQL 8 database PORT must be provided!")
        sys.exit(2)

    if db_usr is None or db_usr.strip() == "":
        print("Database user must be provided!")
        sys.exit(2)

    if db_pw is None or db_pw.strip() == "":
        print("Database password must be provided!")
        sys.exit(2)

    if db_schema is None or db_schema.strip() == "":
        print("Database schema must be provided!")
        sys.exit(2)

    database_helper = DatabaseHelper(db_url, db_port, db_usr, db_pw, db_schema)

    setup_logging(instance_name)

    logging.info("[Main] - dods-match-stats " + instance_name + " started!")

    if input_dir is not None and input_dir != "":
        if input_dir.endswith(os.sep):
            input_dir += "*.log"
        else:
            input_dir = os.path.join(input_dir, "*.log")
        __read_from_logs_folder(database_helper, instance_name, input_dir, output_dir)
    else:
        __read_from_remote_log_listener(database_helper, instance_name, trusted_ip_address, port, output_dir)


def setup_logging(instance_name):
    log_dir = os.path.join(os.getcwd(), 'logs')

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, instance_name + ".log")

    rotating_file_handler = RotatingFileHandler(str(log_file), mode='a', maxBytes=(1024 * 1024 * 5), backupCount=5)
    rotating_file_handler.setFormatter(formatter)

    logger.addHandler(rotating_file_handler)


if __name__ == "__main__":
    main()
