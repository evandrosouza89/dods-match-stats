#!/usr/bin/python3

import getopt
import glob
import logging
import os
import sys

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


def __read_from_remote_log_listener():
    log_listener = RemoteLogListener()
    log_listener.start()
    __event_reader = EventReader(log_listener, __event_processor)
    __event_reader.read()


def main(argv):
    input_dir = ""

    try:
        opts, args = getopt.getopt(argv, "hi:", ["input="])
    except getopt.GetoptError:
        print("Invalid arguments! try dods_match_stats.py -h for help")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Usage example: dods_match_stats.py -i <inputdir>")
            sys.exit()
        elif opt in ("-i", "--input"):
            input_dir = arg

    if input_dir != "":
        if input_dir.endswith(os.sep):
            input_dir += "*.log"
        else:
            input_dir = os.path.join(input_dir, "*.log")
        __read_from_logs_folder(input_dir)
    else:
        logging.info("[Main] - dods-match-status started!")
        __read_from_remote_log_listener()


if __name__ == "__main__":
    main(sys.argv[1:])
