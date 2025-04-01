from .event import Event


# Covers log file 'beginning of file' entry
class BOFEventParser:

    @staticmethod
    def parse_event(time_stamp, file, game, version):
        return BOFEvent(time_stamp, file, game, version)


class BOFEvent(Event):
    def __init__(self, time_stamp, file, game, version):
        Event.__init__(self, time_stamp)
        self.file = file
        self.game = game
        self.version = version
