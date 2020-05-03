import configparser
import logging
import os
import sys

current_directory = os.path.dirname(__file__)
config = configparser.RawConfigParser()
config.read(os.path.join(os.path.split(current_directory)[0], "config_file.properties"))

formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

screen_handler = logging.StreamHandler(stream=sys.stdout)
screen_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(screen_handler)
