import re

from .bof_event_parser import BOFEventParser
from .eof_event_parser import EOFEventParser
from .p2p_action_event_parser import PlayerToPlayerActionEventParser
from .player_action_event_parser import PlayerActionEventParser
from .team_action_event_parser import TeamActionEventParser
from .world_action_event_parser import WorldActionEventParser


class EventProcessor:
    __TIME_STAMP_REGEX = r"(RL|L) (\d{2}\/\d{2}\/\d{4} - \d{2}:\d{2}:\d{2}):"

    __ignored_events_regex = re.compile(__TIME_STAMP_REGEX + r"//")
    __p2p_action_event_regex = re.compile(
        __TIME_STAMP_REGEX + r" \"([^\"]+)\" ([^\"(]+) \"([^\"]+)\" ([^\"(]+) \"([^\"]+)\"(.*)")
    __player_action_event_regex = re.compile(__TIME_STAMP_REGEX + r" \"([^\"]+)\" ([^\"(]+) \"(.+?)\"(.*)")
    __player_action_event_regex2 = re.compile(__TIME_STAMP_REGEX + r" \"([^\"]+)\" ([^(]+)(.*)")
    __team_action_event_regex = re.compile(__TIME_STAMP_REGEX + r" Team \"([^\"]+)\" ([^\"(]+) \"([^\"]+)\"(.*)")
    __world_action_event_regex = re.compile(__TIME_STAMP_REGEX + r" ([^\"(]+) \"([^\"]+)\"(.*)")
    __eof_event_regex = re.compile(__TIME_STAMP_REGEX + r" (Log file closed\.)")
    __bof_event_regex = re.compile(
        __TIME_STAMP_REGEX + r" (Log file started \(file \"(.+)\"\) \(game \"(.+)\"\) \(version \"(.+)\"\))")

    __p2p_action_event_parser = PlayerToPlayerActionEventParser()
    __player_action_event_parser = PlayerActionEventParser()
    __team_action_event_parser = TeamActionEventParser()
    __world_action_event_parser = WorldActionEventParser()
    __eof_event_parser = EOFEventParser()
    __bof_event_parser = BOFEventParser()

    def __init__(self, match_state_processor):
        self.__match_state_processor = match_state_processor

    def process(self, raw_event):
        event = EventProcessor.__process_raw(raw_event)
        if event is not None:
            self.__match_state_processor.process(event)

    @staticmethod
    def __process_raw(raw_event):
        m = EventProcessor.__ignored_events_regex.search(raw_event)

        if not m:
            m = EventProcessor.__p2p_action_event_regex.search(raw_event)
            if m:
                ignored, time_stamp, player, event1, noun1, event2, noun2, properties = m.groups()
                return EventProcessor.__p2p_action_event_parser.parse_event(time_stamp, raw_event, player,
                                                                            event1, noun1,
                                                                            event2, noun2, properties)

            m = EventProcessor.__player_action_event_regex.search(raw_event)
            if m:
                group_list = m.groups()
                time_stamp = group_list[1].strip()
                player = group_list[2].strip()
                event = group_list[3].strip()
                noun = group_list[4].strip()
                properties = group_list[5].strip()
                return EventProcessor.__player_action_event_parser.parse_event(time_stamp, raw_event,
                                                                               player, event, noun,
                                                                               properties)
            m = EventProcessor.__player_action_event_regex2.search(raw_event)
            if m:
                group_list = m.groups()
                time_stamp = group_list[1].strip()
                player = group_list[2].strip()
                event = group_list[3].strip()

                return EventProcessor.__player_action_event_parser.parse_event(time_stamp, raw_event,
                                                                               player, event)

            m = EventProcessor.__team_action_event_regex.search(raw_event)
            if m:
                ignored, time_stamp, team, event, noun, properties = m.groups()
                time_stamp = time_stamp.strip()
                event = event.strip()
                noun = noun.strip()
                properties = properties.strip()
                return EventProcessor.__team_action_event_parser.parse_event(time_stamp, raw_event, team,
                                                                             event, noun, properties)

            m = EventProcessor.__world_action_event_regex.search(raw_event)
            if m:
                ignored, time_stamp, event, noun, properties = m.groups()
                time_stamp = time_stamp.strip()
                event = event.strip()
                noun = noun.strip()
                properties = properties.strip()
                return EventProcessor.__world_action_event_parser.parse_event(time_stamp, raw_event, event,
                                                                              noun,
                                                                              properties)

            m = EventProcessor.__eof_event_regex.search(raw_event)
            if m:
                ignored, time_stamp, event = m.groups()
                time_stamp = time_stamp.strip()
                return EventProcessor.__eof_event_parser.parse_event(time_stamp)

            m = EventProcessor.__bof_event_regex.search(raw_event)
            if m:
                ignored, time_stamp, event, file, game, version = m.groups()
                time_stamp = time_stamp.strip()
                return EventProcessor.__bof_event_parser.parse_event(time_stamp, file, game, version)
