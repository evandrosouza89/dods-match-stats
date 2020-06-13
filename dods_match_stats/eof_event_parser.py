from .event import Event


# Covers log file end of file entry
class EOFEventParser:

    @staticmethod
    def parse_event(time_stamp):
        return EOFEvent(time_stamp)


class EOFEvent(Event):
    def __init__(self, time_stamp):
        Event.__init__(self, time_stamp)
