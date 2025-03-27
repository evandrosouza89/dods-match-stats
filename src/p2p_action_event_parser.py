import logging
import re
from enum import Enum

from .event import Event
from .player_parser import PlayerParser


# Covers events 057, 058 and 059
class PlayerToPlayerActionEventParser:

    @staticmethod
    def parse_event(time_stamp, raw_event, player, event1, noun1, event2, noun2, properties):

        player1 = PlayerParser.parse_player(player)

        if EventEnum.ATTACKED.value == event1:
            player2 = PlayerParser.parse_player(noun1)
            regex = re.compile(r"\(damage \"(\d+?)\"\) \(health \"(\d+?)\"\) \(hitgroup \"(.+?)\"\)")

            m = regex.search(properties)

            damage, health, hit_group = m.groups()

            return AttackEvent(time_stamp, player1, player2, noun2, damage, health, hit_group)

        elif EventEnum.KILLED.value == event1:
            player2 = PlayerParser.parse_player(noun1)
            return KillEvent(time_stamp, player1, player2, noun2)

        elif EventEnum.TRIGGERED.value == event1:
            player2 = PlayerParser.parse_player(noun2)
            if NounEnum.DOMINATION.value == noun1:
                return DominationEvent(time_stamp, player1, player2)
            if NounEnum.REVENGE.value == noun1:
                return RevengeEvent(time_stamp, player1, player2)
            else:
                logging.warning("[PlayerToPlayerActionEventParser] - Event: [" + raw_event + "] discarded!")
                return None

        else:
            logging.warning("[PlayerToPlayerActionEventParser] - Event: [" + raw_event + "] discarded!")
            return None


class EventEnum(Enum):
    ATTACKED = "attacked"
    KILLED = "killed"
    TRIGGERED = "triggered"


class NounEnum(Enum):
    DOMINATION = "domination"
    REVENGE = "revenge"


class HitGroupEnum(Enum):
    HEAD = "head"
    CHEST = "chest"
    GENERIC = "generic"
    RIGHT_LEG = "right leg"
    LEFT_LEG = "left leg"
    RIGHT_ARM = "right arm"
    LEFT_ARM = "left arm"


class AttackEvent(Event):
    def __init__(self, time_stamp, player_attacker, player_attacked, weapon, damage, health, hit_group):
        Event.__init__(self, time_stamp)
        self.player_attacker = player_attacker
        self.player_attacked = player_attacked
        self.weapon = weapon
        self.damage = damage
        self.health = health
        self.hit_group = hit_group


class KillEvent(Event):
    def __init__(self, time_stamp, player_killer, player_killed, weapon):
        Event.__init__(self, time_stamp)
        self.player_killer = player_killer
        self.player_killed = player_killed
        self.weapon = weapon


class DominationEvent(Event):
    def __init__(self, time_stamp, player_dominator, player_dominated):
        Event.__init__(self, time_stamp)
        self.player_dominator = player_dominator
        self.player_dominated = player_dominated


class RevengeEvent(Event):
    def __init__(self, time_stamp, player_avenger, player_killed):
        Event.__init__(self, time_stamp)
        self.player_avenger = player_avenger
        self.player_killed = player_killed
