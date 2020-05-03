#!/usr/bin/python3

import getopt
import glob
import logging
import os
import sys

from dods_match_stats import logger, config
from dods_match_stats.event_processor import EventProcessor
from dods_match_stats.event_reader import EventReader
from dods_match_stats.match_state_processor import MatchStateProcessor
from dods_match_stats.match_stats_processor import MatchStatsProcessor
from dods_match_stats.match_writer import MatchWriter
from dods_match_stats.remote_log_listener import RemoteLogListener

__match_writer = MatchWriter()
__match_stats_processor = MatchStatsProcessor(__match_writer)
__match_state_processor = MatchStateProcessor(__match_stats_processor)
__event_processor = EventProcessor(__match_state_processor)


def __read_from_logs_folder(input_dir):
    file_path_list = glob.glob(input_dir)

    for file_path in file_path_list:
        f = open(file_path, "r", encoding="utf-8", errors='replace')
        __event_reader = EventReader(f, __event_processor)
        __event_reader.read()


def __read_from_remote_log_listener(trusted_ip_address, port):
    log_listener = RemoteLogListener(trusted_ip_address, port)
    log_listener.start()
    __event_reader = EventReader(log_listener, __event_processor)
    __event_reader.read()


def main(argv):
    trusted_ip_address = None
    port = None
    log_file = None
    input_dir = ""

    try:
        opts, args = getopt.getopt(argv, "hi:t:p:l:", ["input=", "trusted_ip_address=", "port="])
    except getopt.GetoptError:
        print("Invalid argument! try dods_match_stats.py -h for help")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(
                "Usage example: 'dods_match_stats.py -i <inputdir>' or (exclusive) 'dods_match_stats.py -t "
                "192.168.1.10 -p 27016'")
            sys.exit()
        elif opt in ("-i", "--input"):
            input_dir = arg
        elif opt in ("-t", "--trusted_ip_address"):
            trusted_ip_address = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-l", "--log_file"):
            log_file = arg
        else:
            print("Invalid argument! try dods_match_stats.py -h for help")
            sys.exit(2)

    if log_file is None:
        file_handler = logging.FileHandler(config.get("LogFileSection", "logfile.path"))
    else:
        file_handler = logging.FileHandler(log_file)

    logger.addHandler(file_handler)

    logging.info("[Main] - dods-match-status started!")

    if input_dir != "":
        if input_dir.endswith(os.sep):
            input_dir += "*.log"
        else:
            input_dir = os.path.join(input_dir, "*.log")
        __read_from_logs_folder(input_dir)
    else:
        __read_from_remote_log_listener(trusted_ip_address, port)


if __name__ == "__main__":
    main(sys.argv[1:])
