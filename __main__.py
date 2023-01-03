#!/usr/bin/python3

import getopt
import glob
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from dods_match_stats import logger, config, formatter
from dods_match_stats.database_helper import DatabaseHelper
from dods_match_stats.event_processor import EventProcessor
from dods_match_stats.event_reader import EventReader
from dods_match_stats.half_processor import HalfProcessor
from dods_match_stats.html_writer import HtmlWriter
from dods_match_stats.match_state_processor import MatchStateProcessor
from dods_match_stats.match_stats_processor import MatchStatsProcessor
from dods_match_stats.match_writer import MatchWriter
from dods_match_stats.remote_log_listener import RemoteLogListener
from dods_match_stats.topic_writer import TopicWriter


def __init(database_helper, instance_name, output_dir, topic_writer_enabled):
    topic_writer = TopicWriter(topic_writer_enabled)
    html_writer = HtmlWriter(output_dir, topic_writer)
    half_processor = HalfProcessor(database_helper, html_writer)
    match_writer = MatchWriter(database_helper, half_processor, instance_name)
    match_stats_processor = MatchStatsProcessor(match_writer)
    match_state_processor = MatchStateProcessor(match_stats_processor)

    return EventProcessor(match_state_processor)


def __read_from_logs_folder(database_helper, instance_name, input_dir, output_dir, topic_writer_enabled):
    file_path_list = glob.glob(input_dir)
    file_path_list.sort()

    for file_path in file_path_list:
        f = open(file_path, "r", encoding="utf-8", errors='replace')
        event_processor = __init(database_helper, instance_name, output_dir, topic_writer_enabled)
        event_reader = EventReader(f, event_processor)
        event_reader.read()


def __read_from_remote_log_listener(database_helper, instance_name, trusted_ip_address, port, output_dir,
                                    topic_writer_enabled):
    log_listener = RemoteLogListener(trusted_ip_address, port)
    log_listener.start()
    event_processor = __init(database_helper, instance_name, output_dir, topic_writer_enabled)
    event_reader = EventReader(log_listener, event_processor)
    event_reader.read()


def main(argv):
    trusted_ip_address = None
    port = None
    log_dir = None
    input_dir = ""
    instance_name = None
    output_dir = ""
    topic_writer_enabled = False
    db_url = None
    db_port = None
    db_usr = ""
    db_pw = None
    db_schema = None

    shortopts = "hi:t:p:l:n:o:fd:q:u:w:s:"
    longopts = ["input=",
                "trusted_ip_address=",
                "port=",
                "log_dir=",
                "instance_name=",
                "output_dir=",
                "forum_enabled=",
                "db_url=",
                "db_port=",
                "db_usr=",
                "db_pw=",
                "db_schema="]

    try:
        opts, args = getopt.getopt(argv, shortopts, longopts)
    except getopt.GetoptError:
        print("Invalid argument! try dods_match_stats.py -h for help")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(
                "Usage example: 'dods_match_stats.py -i <inputdir>' or (exclusive) 'dods_match_stats.py "
                "-t 34.95.187.157 -p 8001 -l /opt/dods-match-stats/logs/ -n dodsbr1 -f -d mydb.mysql.com -q 3306 "
                "-u admin -w password -s schema'")
            sys.exit()
        elif opt in ("-i", "--input"):
            input_dir = arg
        elif opt in ("-t", "--trusted_ip_address"):
            trusted_ip_address = arg
        elif opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-l", "--log_dir"):
            log_dir = arg
        elif opt in ("-n", "--instance_name"):
            instance_name = arg
        elif opt in ("-f", "--forum_enabled"):
            topic_writer_enabled = True
        elif opt in ("-o", "--output_dir"):
            output_dir = arg
        elif opt in ("-d", "--db_url"):
            db_url = arg
        elif opt in ("-q", "--db_port"):
            db_port = int(arg)
        elif opt in ("-u", "--db_usr"):
            db_usr = arg
        elif opt in ("-w", "--db_pw"):
            db_pw = arg
        elif opt in ("-s", "--db_schema"):
            db_schema = arg
        else:
            print("Invalid argument! try dods_match_stats.py -h for help")
            sys.exit(2)

    if instance_name is None or instance_name.strip() == "":
        instance_name = config.get("InstanceInfoSection", "instance.name")

    if instance_name is None or instance_name.strip() == "":
        print("Instance name must be provided!")
        sys.exit(2)

    if output_dir is None or output_dir.strip() == "":
        output_dir = config.get("HTMLPageOutputSection", "output.dir")

    if output_dir is None or output_dir.strip() == "":
        print("Output directory must be provided!")
        sys.exit(2)

    if trusted_ip_address is None or trusted_ip_address.strip() == "":
        trusted_ip_address = config.get("LogListenerSection", "gameserver.address")

    if trusted_ip_address is None or trusted_ip_address.strip() == "":
        print("Game server IP must be provided!")
        sys.exit(2)

    if port is None:
        port = int(config.get("LogListenerSection", "loglistener.port"))

    if port is None or port < 1 or port > 65535:
        print("Database PORT must be provided!")
        sys.exit(2)

    if db_url is None or db_url.strip() == "":
        db_url = config.get("DatabaseSection", "database.url")

    if db_url is None or db_url.strip() == "":
        print("Database URL must be provided!")
        sys.exit(2)

    if db_port is None:
        db_port = int(config.get("DatabaseSection", "database.port"))

    if db_port is None or db_port < 1 or db_port > 65535:
        print("Database PORT must be provided!")
        sys.exit(2)

    if db_usr is None or db_usr.strip() == "":
        db_usr = config.get("DatabaseSection", "database.user")

    if db_usr is None or db_usr.strip() == "":
        print("Database user must be provided!")
        sys.exit(2)

    if db_pw is None or db_pw.strip() == "":
        db_pw = config.get("DatabaseSection", "database.password")

    if db_pw is None or db_pw.strip() == "":
        print("Database password must be provided!")
        sys.exit(2)

    if db_schema is None or db_schema.strip() == "":
        db_schema = config.get("DatabaseSection", "database.schema")

    if db_schema is None or db_schema.strip() == "":
        print("Database schema must be provided!")
        sys.exit(2)

    database_helper = DatabaseHelper(db_url, db_port, db_usr, db_pw, db_schema)

    if log_dir is None:
        log_dir = config.get("InstanceInfoSection", "logdir.path")

    log_file = os.path.join(log_dir, instance_name + ".log")

    rotating_file_handler = RotatingFileHandler(log_file, mode='a', maxBytes=(1024 * 1024 * 5), backupCount=5)
    rotating_file_handler.setFormatter(formatter)
    logger.addHandler(rotating_file_handler)

    logging.info("[Main] - dods-match-stats " + instance_name + " started!")

    if input_dir != "":
        if input_dir.endswith(os.sep):
            input_dir += "*.log"
        else:
            input_dir = os.path.join(input_dir, "*.log")
        __read_from_logs_folder(database_helper, instance_name, input_dir, output_dir, topic_writer_enabled)
    else:
        __read_from_remote_log_listener(database_helper, instance_name, trusted_ip_address, port, output_dir,
                                        topic_writer_enabled)


if __name__ == "__main__":
    main(sys.argv[1:])
