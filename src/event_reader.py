import logging
from io import IOBase


class EventReader:

    def __init__(self, source, processor):
        self.__source = source
        self.__processor = processor

    def read(self):
        if isinstance(self.__source, IOBase):  # File Reader
            try:
                contents = self.__source.readlines()
                for line in contents:
                    self.__processor.process(line)
            except Exception as e:
                logging.exception("[EventReader] - Exception occurred: [" + repr(e) + "]")

        else:  # UDP Listener
            while True:
                try:
                    contents = self.__source.get_message()
                    logging.info("[EventReader] - " + contents)
                    self.__processor.process(contents)
                except Exception as e:
                    logging.exception("[EventReader] - Exception occurred: [" + repr(e) + "]")
