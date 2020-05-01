import logging
import queue
import socket
from threading import Thread

from . import config


class RemoteLogListener(Thread):
    __END_OF_MESSAGE = bytearray('\x00\n', 'utf-8')
    __port_from_config = int(config.get("LogListenerSection", "loglistener.port"))
    __trusted_address = config.get("LogListenerSection", "gameserver.address")

    def __init__(self, port):
        Thread.__init__(self)
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__port = None
        if port is not None:
            self.__port = int(port)
        else:
            self.__port = RemoteLogListener.__port_from_config
        self.__server_socket.bind(("0.0.0.0", self.__port))
        self.__incomplete_message = None
        self.__message_queue = queue.Queue()

    def get_message(self):
        return self.__message_queue.get()

    def __process_buffer(self, buffer):

        if self.__incomplete_message is not None:
            buffer = self.__incomplete_message + buffer

        last_index = len(buffer)

        reversed_buffer = buffer[::-1]

        found_eom = False

        for i in range(len(reversed_buffer)):
            if not found_eom and reversed_buffer[i:i + 2] == RemoteLogListener.__END_OF_MESSAGE:
                last_index = i
                found_eom = True

        self.__incomplete_message = buffer[len(buffer) - last_index:len(buffer)]

        if found_eom:
            buffer = buffer[0: len(buffer) - last_index]

            message_list = buffer.decode("utf-8", errors='ignore').split("\n\x00")

            for message in message_list:
                if message != "":
                    self.__message_queue.put(message)

    def run(self):
        logging.info("[RemoteLogListener] - Listening for logs at port: " + str(self.__port))
        while True:
            buffer, address = self.__server_socket.recvfrom(65535)

            logging.debug("[RemoteLogListener] - Received: [" + buffer.decode("utf-8", errors='ignore')
                          + "] from " + address[0] + ":" + str(address[1]))

            if address[0] == RemoteLogListener.__trusted_address:
                RemoteLogListener.__process_buffer(self, buffer)
            else:
                logging.warning("[RemoteLogListener] - Discarded: [" + buffer.decode("utf-8", errors='ignore')
                                + "] from " + address[0] + ":" + str(address[1]))
