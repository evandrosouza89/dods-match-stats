import logging
import re
from enum import Enum

from .event import Event


# Covers events 003 and 062
class WorldActionEventParser:

    @staticmethod
    def parse_event(time_stamp, raw_event, event, noun, properties):

        if EventEnum.LOADING_MAP.value == event:
            return MapLoadingEvent(time_stamp, noun)

        elif EventEnum.STARTED_MAP.value == event:
            return StartedMapEvent(time_stamp, noun)

        elif EventEnum.WORLD_TRIGGERED.value == event:
            if NounEnum.GAME_OVER.value == noun:
                regex = re.compile(r"reason \"(.+?)\"")

                m = regex.search(properties)

                reason = m.groups()[0]

                return GameOverEvent(time_stamp, reason)

            elif NounEnum.READY_RESTART_BEGIN.value == noun:
                return ReadyRestartBeginEvent(time_stamp)

            elif NounEnum.ROUND_START.value == noun:
                return RoundStartEvent(time_stamp)

            elif NounEnum.ROUND_RESTART.value == noun:
                return RoundRestartEvent(time_stamp)

            elif NounEnum.AXIS_READY.value == noun:
                return AxisReadyEvent(time_stamp)

            elif NounEnum.ALLIES_READY.value == noun:
                return AlliesReadyEvent(time_stamp)

            elif NounEnum.WARMUP_BEGIN.value == noun:
                return WarmupBeginEvent(time_stamp)

            elif NounEnum.WARMUP_ENDS.value == noun:
                return WarmupEndsEvent(time_stamp)

            else:
                logging.warning("[WorldActionEventParser] - Event: [" + raw_event + "] discarded!")

        elif EventEnum.SERVER_CVAR.value == event:
            regex = re.compile(r"\"(.+?)\"")

            m = regex.search(properties)

            if m is not None:
                value = m.groups()[0]
            else:
                value = ""
            return ServerCvarEvent(time_stamp, noun, value)

        else:
            if event != "server_cvar:":
                logging.warning("[WorldActionEventParser] - Event: [" + raw_event + "] discarded!")
            return None


class EventEnum(Enum):
    LOADING_MAP = "Loading map"
    STARTED_MAP = "Started map"
    WORLD_TRIGGERED = "World triggered"
    SERVER_CVAR = "server_cvar:"


class NounEnum(Enum):
    READY_RESTART_BEGIN = "Ready_Restart_Begin"
    ROUND_RESTART = "Round_Restart"
    ROUND_START = "Round_Start"
    AXIS_READY = "Axis Ready"
    ALLIES_READY = "Allies Ready"
    WARMUP_BEGIN = "Warmup_Begin"
    WARMUP_ENDS = "Warmup_Ends"
    GAME_OVER = "Game_Over"
    SM_NEXTMAP = "sm_nextmap"


class ReasonEnum(Enum):
    REASON = "Reached Time Limit"


class MapLoadingEvent(Event):
    def __init__(self, time_stamp, map_name):
        Event.__init__(self, time_stamp)
        self.map_name = map_name


class StartedMapEvent(Event):
    def __init__(self, time_stamp, map_name):
        Event.__init__(self, time_stamp)
        self.map_name = map_name


class GameOverEvent(Event):
    def __init__(self, time_stamp, reason):
        Event.__init__(self, time_stamp)
        self.reason = reason


class WorldTriggeredEvent(Event):
    def __init__(self, time_stamp):
        Event.__init__(self, time_stamp)


class ServerCvarEvent(Event):
    def __init__(self, time_stamp, server_cvar, value):
        Event.__init__(self, time_stamp)
        self.server_cvar = server_cvar
        self.value = value


class RoundStartEvent(WorldTriggeredEvent):
    def __init__(self, time_stamp):
        WorldTriggeredEvent.__init__(self, time_stamp)


class ReadyRestartBeginEvent(WorldTriggeredEvent):
    def __init__(self, time_stamp):
        WorldTriggeredEvent.__init__(self, time_stamp)


class RoundRestartEvent(WorldTriggeredEvent):
    def __init__(self, time_stamp):
        WorldTriggeredEvent.__init__(self, time_stamp)


class AxisReadyEvent(WorldTriggeredEvent):
    def __init__(self, time_stamp):
        WorldTriggeredEvent.__init__(self, time_stamp)


class AlliesReadyEvent(WorldTriggeredEvent):
    def __init__(self, time_stamp):
        WorldTriggeredEvent.__init__(self, time_stamp)


class WarmupBeginEvent(WorldTriggeredEvent):
    def __init__(self, time_stamp):
        WorldTriggeredEvent.__init__(self, time_stamp)


class WarmupEndsEvent(WorldTriggeredEvent):
    def __init__(self, time_stamp):
        WorldTriggeredEvent.__init__(self, time_stamp)
