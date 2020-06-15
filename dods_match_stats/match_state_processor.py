import logging

from .eof_event_parser import EOFEvent
from .match import Match
from .p2p_action_event_parser import AttackEvent, KillEvent, DominationEvent, RevengeEvent
from .player_action_event_parser import ConnectionEvent, DisconnectionEvent, EnteredTheGameEvent, \
    SteamUserIdValidatedEvent, SuicideEvent, JoinedTeamEvent, ChangedRoleEvent, ChangedNameEvent, SayEvent, \
    SayTeamEvent, CapBlockEvent
from .team_action_event_parser import TeamEnum, CapturedLocEvent, RoundWinEvent, TickScoreEvent
from .world_action_event_parser import MapLoadingEvent, StartedMapEvent, GameOverEvent, RoundStartEvent, \
    WarmupEndsEvent, RoundRestartEvent, WarmupBeginEvent, AxisReadyEvent, AlliesReadyEvent, ServerCvarEvent, NounEnum


class MatchStateProcessor:

    def __init__(self, match_stats_processor):
        self.__match_stats_processor = match_stats_processor
        self.__match = None
        self.__spectators = set()
        self.__last_round_events = []

    def process(self, event):
        if type(event) in (MapLoadingEvent, StartedMapEvent):
            self.__stop_match()
            self.__match = Match(None, None, event.map_name)
            self.__spectators = set()

        elif type(event) == ServerCvarEvent:
            if event.server_cvar == NounEnum.SM_NEXTMAP.value:
                if self.__match is None:
                    self.__match = Match(None, None, event.value)
                elif self.__match.map_name is None:
                    self.__match.map_name = event.value

        elif type(event) in (WarmupBeginEvent, AxisReadyEvent, AlliesReadyEvent):
            self.__stop_match()

        elif type(event) == RoundRestartEvent:
            self.__stop_match()
            self.__last_round_events.append(event)

        elif type(event) == WarmupEndsEvent:
            self.__last_round_events.append(event)

        elif type(event) == RoundStartEvent:
            if len(self.__last_round_events) >= 2:
                if type(self.__last_round_events[-1]) == WarmupEndsEvent:
                    if type(self.__last_round_events[-2]) == RoundRestartEvent:
                        self.__match.start_time_stamp = event.time_stamp
                        self.__last_round_events = []

                        logging.info("[MatchStateProcessor] - New match started! Now processing events.")

        elif type(event) in (ConnectionEvent, EnteredTheGameEvent, SteamUserIdValidatedEvent):
            if event.player.uid != "0":
                self.__spectators.add(event.player)

        elif type(event) == EOFEvent:
            if self.__is_match_valid():
                logging.info("[MatchStateProcessor] - Match ended! Now closing stats!")
                self.__match.spectators = self.__spectators
                self.__match_stats_processor.close_stats(event)
            self.__stop_match()

        elif self.__is_match_started():
            event.match = self.__match

            if type(event) == GameOverEvent:
                self.__match.end_time_stamp = event.time_stamp

            # player to player action events
            elif type(event) == AttackEvent:
                self.__match.attack_event_list.append(event)
                self.__manage_player_list(event.player_attacker)
                self.__manage_player_list(event.player_attacked)

            elif type(event) == KillEvent:
                self.__match.kill_event_list.append(event)

            elif type(event) == DominationEvent:
                self.__match.domination_event_list.append(event)

            elif type(event) == RevengeEvent:
                self.__match.revenge_event_list.append(event)

            # player action events
            elif type(event) == ConnectionEvent:
                self.__match.connection_event_list.append(event)

            elif type(event) == DisconnectionEvent:
                self.__match.disconnection_event_list.append(event)

            elif type(event) == EnteredTheGameEvent:
                self.__match.entered_the_game_event_list.append(event)

            elif type(event) == SteamUserIdValidatedEvent:
                self.__match.steam_user_id_validated_event_list.append(event)

            elif type(event) == SuicideEvent:
                self.__match.suicide_event_list.append(event)

            elif type(event) == JoinedTeamEvent:
                self.__match.joined_team_event_list.append(event)
                event.player.team = event.team
                self.__manage_player_list(event.player)

            elif type(event) == ChangedRoleEvent:
                self.__match.changed_role_event_list.append(event)

            elif type(event) == ChangedNameEvent:
                self.__match.changed_name_event_list.append(event)
                self.__manage_player_list(event.player)

            elif type(event) == SayEvent:
                if event.player.uid != "0":
                    self.__match.say_event_list.append(event)
                    self.__manage_player_list(event.player)

            elif type(event) == SayTeamEvent:
                self.__match.say_team_event_list.append(event)

            elif type(event) == CapBlockEvent:
                self.__match.cap_block_event_list.append(event)
                self.__manage_player_list(event.player)

            # team action events
            elif type(event) == CapturedLocEvent:
                self.__match.captured_loc_event_list.append(event)
                for player in event.player_list:
                    self.__manage_player_list(player)

            elif type(event) == RoundWinEvent:
                self.__match.round_win_event_list.append(event)

                if TeamEnum.AXIS.value == event.team:
                    self.__match.team_axis_team_score = event.rounds_won
                else:
                    self.__match.team_allies_team_score = event.rounds_won

            elif type(event) == TickScoreEvent:
                self.__match.tick_score_event_list.append(event)

                if TeamEnum.AXIS.value == event.team:
                    self.__match.team_axis_tick_score = event.total_score
                else:
                    self.__match.team_allies_tick_score = event.total_score

            self.__match_stats_processor.update_stats(event)

    def __stop_match(self):
        current_map_name = None
        if self.__match is not None:
            current_map_name = self.__match.map_name
        self.__match = None
        self.__last_round_events = []
        self.__match = Match(None, None, current_map_name)
        self.__match_stats_processor.reset_stats(self.__match)

        logging.debug("[MatchStateProcessor] - Match state cleared.")

    def __is_match_started(self):
        if self.__match is None:
            return False

        if self.__match.start_time_stamp is None:
            return False

        if self.__match.map_name is None:
            return False

        return True

    def __is_match_valid(self):
        if self.__is_match_started():
            if None in (self.__match.team_allies_tick_score,
                    self.__match.team_axis_tick_score,
                    self.__match.end_time_stamp):
                return False
        else:
            return False
        return True

    def __manage_player_list(self, player):
        if player.team == TeamEnum.ALLIES.value:
            self.__match.team_allies_players.add(player)
            if player in self.__spectators:
                self.__spectators.remove(player)
        elif player.team == TeamEnum.AXIS.value:
            self.__match.team_axis_players.add(player)
            if player in self.__spectators:
                self.__spectators.remove(player)
        elif player.uid != "0":
            self.__spectators.add(player)
