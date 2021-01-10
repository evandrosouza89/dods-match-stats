#!/usr/bin/python3

import getopt
import glob
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from dods_match_stats import logger, config, formatter
from dods_match_stats.event_processor import EventProcessor
from dods_match_stats.event_reader import EventReader
from dods_match_stats.half_processor import HalfProcessor
from dods_match_stats.html_writer import HtmlWriter
from dods_match_stats.match_state_processor import MatchStateProcessor
from dods_match_stats.match_stats_processor import MatchStatsProcessor
from dods_match_stats.match_writer import MatchWriter
from dods_match_stats.remote_log_listener import RemoteLogListener
from dods_match_stats.topic_writer import TopicWriter


def __init(instance_name, topic_writer_enabled):
    topic_writer = TopicWriter(topic_writer_enabled)
    html_writer = HtmlWriter(topic_writer)
    half_processor = HalfProcessor(html_writer)
    match_writer = MatchWriter(instance_name, half_processor)
    match_stats_processor = MatchStatsProcessor(match_writer)
    match_state_processor = MatchStateProcessor(match_stats_processor)
    return EventProcessor(match_state_processor)


def __read_from_logs_folder(instance_name, input_dir, topic_writer_enabled):
    file_path_list = glob.glob(input_dir)
    file_path_list.sort()

    for file_path in file_path_list:
        f = open(file_path, "r", encoding="utf-8", errors='replace')
        event_processor = __init(instance_name, topic_writer_enabled)
        event_reader = EventReader(f, event_processor)
        event_reader.read()


def __read_from_remote_log_listener(instance_name, trusted_ip_address, port, topic_writer_enabled):
    log_listener = RemoteLogListener(trusted_ip_address, port)
    log_listener.start()
    event_processor = __init(instance_name, topic_writer_enabled)
    event_reader = EventReader(log_listener, event_processor)
    event_reader.read()


def main(argv):
    trusted_ip_address = None
    port = None
    log_dir = None
    input_dir = ""
    instance_name = None
    topic_writer_enabled = False

    try:
        opts, args = getopt.getopt(argv, "hi:t:p:l:n:f:", ["input=", "trusted_ip_address=", "port="])
    except getopt.GetoptError:
        print("Invalid argument! try dods_match_stats.py -h for help")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(
                "Usage example: 'dods_match_stats.py -i <inputdir>' or (exclusive) 'dods_match_stats.py "
                "-t 34.95.187.157 -p 8001 -l /opt/dods-match-stats/logs/ -n dodsbr1 -f'")
            sys.exit()
        elif opt in ("-i", "--input"):
            input_dir = arg
        elif opt in ("-t", "--trusted_ip_address"):
            trusted_ip_address = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-l", "--log_dir"):
            log_dir = arg
        elif opt in ("-n", "--instance_name"):
            instance_name = arg
        elif opt in ("-f", "--forum_enabled"):
            topic_writer_enabled = True
        else:
            print("Invalid argument! try dods_match_stats.py -h for help")
            sys.exit(2)

    if instance_name is None or instance_name.strip() == "":
        instance_name = config.get("InstanceInfoSection", "instance.name")

    if instance_name is None or instance_name.strip() == "":
        print("Instance name must be provided!")
        sys.exit(2)

    if log_dir is None:
        log_dir = os.path.join(config.get("InstanceInfoSection", "logdir.path"), "logs")

    log_file = os.path.join(log_dir, instance_name + ".log")

    rotating_file_handler = RotatingFileHandler(log_file, mode='a', maxBytes=(1024 * 1024 * 5), backupCount=5)
    rotating_file_handler.setFormatter(formatter)
    logger.addHandler(rotating_file_handler)

    logging.info("[Main] - dods-match-status " + instance_name + " started!")

    if input_dir != "":
        if input_dir.endswith(os.sep):
            input_dir += "*.log"
        else:
            input_dir = os.path.join(input_dir, "*.log")
        __read_from_logs_folder(instance_name, input_dir, topic_writer_enabled)
    else:
        __read_from_remote_log_listener(instance_name, trusted_ip_address, port, topic_writer_enabled)


if __name__ == "__main__":
    main(sys.argv[1:])
