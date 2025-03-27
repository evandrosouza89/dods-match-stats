import logging
import re
from enum import Enum

from .event import Event
from .player_parser import PlayerParser


# Covers events 050, 050b, 051, 052, 053, 054, 055, 056, 060, 063
class PlayerActionEventParser:

    @staticmethod
    def parse_event(time_stamp, raw_event, player, event, noun=None, properties=None):

        if EventEnum.DISCONNECTED.value == event:
            player = PlayerParser.parse_player(player)
            return DisconnectionEvent(time_stamp, player)

        elif EventEnum.STEAM_USERID_VALIDATED.value == event:
            player = PlayerParser.parse_player(player)
            return SteamUserIdValidatedEvent(time_stamp, player)

        elif EventEnum.ENTERED_THE_GAME.value == event:
            player = PlayerParser.parse_player(player)
            return EnteredTheGameEvent(time_stamp, player)

        elif EventEnum.CONNECTED_ADDRESS.value == event:
            player = PlayerParser.parse_player(player)
            return ConnectionEvent(time_stamp, player, noun)

        elif EventEnum.COMMITTED_SUICIDE_WITH.value == event:
            player = PlayerParser.parse_player(player)
            return SuicideEvent(time_stamp, player, noun)

        elif EventEnum.JOINED_TEAM.value == event:
            player = PlayerParser.parse_player(player)
            return JoinedTeamEvent(time_stamp, player, noun)

        elif EventEnum.CHANGED_ROLE_TO.value == event:
            player = PlayerParser.parse_player(player)
            return ChangedRoleEvent(time_stamp, player, noun)

        elif EventEnum.CHANGED_NAME_TO.value == event:
            player = PlayerParser.parse_player(player)
            return ChangedNameEvent(time_stamp, player, noun)

        elif EventEnum.SAY.value == event:
            player = PlayerParser.parse_player(player)
            return SayEvent(time_stamp, player, noun)

        elif EventEnum.SAY_TEAM.value == event:
            player = PlayerParser.parse_player(player)
            return SayTeamEvent(time_stamp, player, noun)

        elif EventEnum.TRIGGERED.value == event:
            player = PlayerParser.parse_player(player)

            if NounEnum.CAP_BLOCK.value == noun:
                regex = re.compile(r"\(flagindex \"(\d+)\"\) \(flagname \"(.*?)\"\)")

                m = regex.search(properties)

                flag_index, flag_name = m.groups()

                return CapBlockEvent(time_stamp, player, flag_index, flag_name)
            else:
                logging.warning("[PlayerActionEventParser] - Event: [" + raw_event + "] discarded!")
                return None

        else:
            if event not in ("=", "= \"\""):
                logging.warning("[PlayerActionEventParser] - Event: [" + raw_event + "] discarded!")
            return None


class EventEnum(Enum):
    DISCONNECTED = "disconnected"
    STEAM_USERID_VALIDATED = "STEAM USERID validated"
    ENTERED_THE_GAME = "entered the game"
    CONNECTED_ADDRESS = "connected, address"
    COMMITTED_SUICIDE_WITH = "committed suicide with"
    JOINED_TEAM = "joined team"
    CHANGED_ROLE_TO = "changed role to"
    CHANGED_NAME_TO = "changed name to"
    SAY = "say"
    SAY_TEAM = "say_team"
    TRIGGERED = "triggered"


class NounEnum(Enum):
    CAP_BLOCK = "capblock"


class PlayerEvent(Event):
    def __init__(self, time_stamp, player):
        Event.__init__(self, time_stamp)
        self.player = player


class ConnectionEvent(PlayerEvent):
    def __init__(self, time_stamp, player, ip_address):
        PlayerEvent.__init__(self, time_stamp, player)
        self.ip_address = ip_address


class DisconnectionEvent(PlayerEvent):
    def __init__(self, time_stamp, player):
        PlayerEvent.__init__(self, time_stamp, player)


class EnteredTheGameEvent(PlayerEvent):
    def __init__(self, time_stamp, player):
        PlayerEvent.__init__(self, time_stamp, player)


class SteamUserIdValidatedEvent(PlayerEvent):
    def __init__(self, time_stamp, player):
        PlayerEvent.__init__(self, time_stamp, player)


class SuicideEvent(PlayerEvent):
    def __init__(self, time_stamp, player, weapon):
        PlayerEvent.__init__(self, time_stamp, player)
        self.weapon = weapon


class JoinedTeamEvent(PlayerEvent):
    def __init__(self, time_stamp, player, team):
        PlayerEvent.__init__(self, time_stamp, player)
        self.team = team


class ChangedRoleEvent(PlayerEvent):
    def __init__(self, time_stamp, player, role):
        PlayerEvent.__init__(self, time_stamp, player)
        self.role = role


class ChangedNameEvent(PlayerEvent):
    def __init__(self, time_stamp, player, name):
        PlayerEvent.__init__(self, time_stamp, player)
        self.name = name


class SayEvent(PlayerEvent):
    def __init__(self, time_stamp, player, message):
        PlayerEvent.__init__(self, time_stamp, player)
        self.message = message


class SayTeamEvent(PlayerEvent):
    def __init__(self, time_stamp, player, message):
        PlayerEvent.__init__(self, time_stamp, player)
        self.message = message


class CapBlockEvent(PlayerEvent):
    def __init__(self, time_stamp, player, flag_index, flag_name):
        PlayerEvent.__init__(self, time_stamp, player)
        self.flag_index = flag_index
        self.flag_name = flag_name
