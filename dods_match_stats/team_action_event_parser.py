import logging
import re
from enum import Enum

from .event import Event
from .player_parser import PlayerParser


# Covers event 061
class TeamActionEventParser:

    @staticmethod
    def parse_event(time_stamp, raw_event, team, event, noun, properties):
        if NounEnum.CAPTURED_LOC.value == noun:
            return TeamActionEventParser.__parse_capture_loc_event(time_stamp, team, properties)
        elif NounEnum.ROUND_WIN.value == noun:
            return TeamActionEventParser.__parse_round_win_event(time_stamp, team, properties)
        elif NounEnum.TEAM_SCORES.value == noun:
            return TeamActionEventParser.__parse_team_scores_event(time_stamp, team, properties)
        elif NounEnum.TICK_SCORE.value == noun:
            return TeamActionEventParser.__parse_tick_score_event(time_stamp, team, properties)
        else:
            logging.warning("[TeamActionEventParser] - Event: [" + raw_event + "] discarded!")
            return None

    @staticmethod
    def __parse_capture_loc_event(time_stamp, team, properties):

        regex = re.compile(r"\(flagindex \"(\d+)\"\) \(flagname \"(.*?)\"\) \(numplayers \"(\d+)\"\) (\(.+\))")

        m = regex.search(properties)

        flag_index, flag_name, num_players, players = m.groups()

        player_list = PlayerParser.parse_player_list(players)

        return CapturedLocEvent(time_stamp, team, flag_index, flag_name, num_players, player_list)

    @staticmethod
    def __parse_round_win_event(time_stamp, team, properties):

        regex = re.compile(r"\(rounds_won \"(\d+)\"\) \(numplayers \"(\d+)\"\)")

        m = regex.search(properties)

        rounds_won, num_players = m.groups()

        return RoundWinEvent(time_stamp, team, rounds_won, num_players)

    @staticmethod
    def __parse_team_scores_event(time_stamp, team, properties):

        regex = re.compile(r"\(roundswon \"(\d+)\"\) \(tickpoints \"(\d+)\"\) \(numplayers \"(\d+)\"\)")

        m = regex.search(properties)

        rounds_won, tick_points, num_players = m.groups()

        return TeamScoresEvent(time_stamp, team, rounds_won, tick_points, num_players)

    @staticmethod
    def __parse_tick_score_event(time_stamp, team, properties):

        regex = re.compile(r"\(score \"(\d+)\"\) \(totalscore \"(\d+)\"\) \(numplayers \"(\d+)\"\)")

        m = regex.search(properties)

        score, total_score, num_players = m.groups()

        return TickScoreEvent(time_stamp, team, score, total_score, num_players)


class NounEnum(Enum):
    CAPTURED_LOC = "captured_loc"
    ROUND_WIN = "round_win"
    TEAM_SCORES = "team_scores"
    TICK_SCORE = "tick_score"


class TeamEnum(Enum):
    ALLIES = "Allies"
    AXIS = "Axis"
    SPECTATOR = "Spectator"
    CONSOLE = "Console"


class CapturedLocEvent(Event):
    def __init__(self, time_stamp, team, flag_index, flag_name, num_players, player_list):
        Event.__init__(self, time_stamp)
        self.team = team
        self.flag_index = flag_index
        self.flag_name = flag_name
        self.num_players = num_players
        self.player_list = player_list


class RoundWinEvent(Event):
    def __init__(self, time_stamp, team, rounds_won, num_players):
        Event.__init__(self, time_stamp)
        self.team = team
        self.rounds_won = rounds_won
        self.num_players = num_players


class TeamScoresEvent(Event):
    def __init__(self, time_stamp, team, rounds_won, tick_points, num_players):
        Event.__init__(self, time_stamp)
        self.team = team
        self.rounds_won = rounds_won
        self.tick_points = tick_points
        self.num_players = num_players


class TickScoreEvent(Event):
    def __init__(self, time_stamp, team, score, total_score, num_players):
        Event.__init__(self, time_stamp)
        self.team = team
        self.score = score
        self.total_score = total_score
        self.num_players = num_players
