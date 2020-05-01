import configparser
import logging
import os

current_directory = os.path.dirname(__file__)
config = configparser.RawConfigParser()
config.read(os.path.join(os.path.split(current_directory)[0], "config_file.properties"))

logger = logging.getLogger()

logging.basicConfig(
    format='%(asctime)s %(levelname)-s %(message)s',
    level=logging.INFO,
    datefmt='%d-%m-%Y %H:%M:%S')

logger.setLevel(logging.INFO)
