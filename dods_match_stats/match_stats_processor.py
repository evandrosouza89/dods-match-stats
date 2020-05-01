import logging

from .match_stat import ADRStat, KillStat, TeamScoreStat, WeaponStat, StreakStat
from .p2p_action_event_parser import AttackEvent, KillEvent, HitGroupEnum
from .player_action_event_parser import SuicideEvent, CapBlockEvent
from .team_action_event_parser import CapturedLocEvent, RoundWinEvent
from .world_action_event_parser import GameOverEvent


class MatchStatsProcessor:

    def __init__(self, match_writer):
        self.__match_writer = match_writer
        self.__match = None
        self.__reset()

    def update_stats(self, event):
        for stat_processor in self.__stat_processor_list:
            stat_processor.process(event)

        for stat_processor in self.__stat_processor_list:
            stat_processor.update(event)

    def __reset(self):
        self.__match = None

        self.__adr_stats = {}
        self.__kill_stats = {}
        self.__team_score_stats = {}
        self.__weapon_stats = {}
        self.__streak_stats = {}

        self.__adr_stats_processor = ADRStatsProcessor(self)
        self.__kill_stats_processor = KillStatsProcessor(self)
        self.__team_score_stats_processor = TeamScoreStatsProcessor(self)
        self.__weapon_stats_processor = WeaponStatsProcessor(self)
        self.__streak_stats_processor = StreakStatsProcessor(self)

        self.__stat_processor_list = [self.__adr_stats_processor, self.__kill_stats_processor,
                                      self.__team_score_stats_processor, self.__weapon_stats_processor,
                                      self.__streak_stats_processor]

    def reset_stats(self, match):
        self.__reset()
        self.__match = match

    def close_stats(self, event):
        self.__streak_stats_processor.process(event)

        logging.info("[MatchStatsProcessor] - Match stats computed! Writing to database.")

        self.__match_writer.write(self.__match)
        self.reset_stats(None)

    def get_kill_stat(self, player):
        kill_stat = self.__kill_stats.get(player.id3)

        if kill_stat is None:
            kill_stat = KillStat(self.__match, player)
            self.__kill_stats[player.id3] = kill_stat
            self.__match.kill_stat_list.append(kill_stat)

        return kill_stat

    def get_adr_stat(self, player):
        adr_stat = self.__adr_stats.get(player.id3)

        if adr_stat is None:
            adr_stat = ADRStat(self.__match, player)
            self.__adr_stats[player.id3] = adr_stat
            self.__match.adr_stat_list.append(adr_stat)

        return adr_stat

    def get_team_score_stat(self, player):
        team_score_stat = self.__team_score_stats.get(player.id3)

        if team_score_stat is None:
            team_score_stat = TeamScoreStat(self.__match, player)
            self.__team_score_stats[player.id3] = team_score_stat
            self.__match.team_score_stat_list.append(team_score_stat)

        return team_score_stat

    def get_weapon_stat(self, player, weapon):
        key = player.id3 + " - " + weapon
        weapon_stat = self.__weapon_stats.get(key)

        if weapon_stat is None:
            weapon_stat = WeaponStat(self.__match, player, weapon)
            self.__weapon_stats[key] = weapon_stat
            self.__match.weapon_stat_list.append(weapon_stat)

        return weapon_stat

    def get_streak_stat(self, player, players_killed):
        key = player.id3 + " - " + str(players_killed)
        streak_stat = self.__streak_stats.get(key)

        if streak_stat is None:
            streak_stat = StreakStat(self.__match, player, players_killed)
            self.__streak_stats[key] = streak_stat
            self.__match.streak_stat_list.append(streak_stat)

        return streak_stat


class StatProcessor(object):
    def __init__(self, parent):
        self._parent = parent

    def process(self, event):
        pass

    def update(self, event):
        pass


class ADRStatsProcessor(StatProcessor):
    def __init__(self, parent):
        StatProcessor.__init__(self, parent)

    def process(self, event):
        if type(event) == AttackEvent:
            self.__process_attack_event(event.player_attacker, event.player_attacked, event.damage)

    def update(self, event):
        if type(event) == KillEvent:
            self.__update_by_kill_event(event.player_killed)

    def __process_attack_event(self, player_attacker, player_attacked, damage):
        adr_stat = self._parent.get_adr_stat(player_attacker)

        if player_attacker.team != player_attacked.team:
            adr_stat.enemy_damage += int(damage)
        else:
            adr_stat.team_damage += int(damage)

    def __update_by_kill_event(self, player_killed):
        adr_stat = self._parent.get_adr_stat(player_killed)
        kill_stat = self._parent.get_kill_stat(player_killed)
        adr_stat.average_damage = adr_stat.enemy_damage / kill_stat.deaths


class KillStatsProcessor(StatProcessor):
    def __init__(self, parent):
        StatProcessor.__init__(self, parent)
        self.__last_attack = None

    def process(self, event):
        if type(event) == KillEvent:
            self.__process_kill_event(event.player_killer, event.player_killed)
        elif type(event) == SuicideEvent:
            self.__process_suicide_event(event.player)
        elif type(event) == AttackEvent:
            self.__last_attack = event

    def __process_kill_event(self, player_killer, player_killed):
        kill_stat = self._parent.get_kill_stat(player_killer)

        if player_killer.team != player_killed.team:
            kill_stat.kills += 1
        else:
            kill_stat.team_kills += 1

        if self.__last_attack is not None \
                and HitGroupEnum.HEAD.value == self.__last_attack.hit_group \
                and self.__last_attack.player_attacker == player_killer \
                and player_killer.team != player_killed.team:
            kill_stat.kills_by_head_shot += 1

        kill_stat = self._parent.get_kill_stat(player_killed)
        kill_stat.deaths += 1

        if player_killer.team == player_killed.team:
            kill_stat.killed_by_team += 1

        if self.__last_attack is not None \
                and HitGroupEnum.HEAD.value == self.__last_attack.hit_group \
                and self.__last_attack.player_attacked == player_killed:
            kill_stat.deaths_by_head_shot += 1

    def __process_suicide_event(self, player):
        kill_stat = self._parent.get_kill_stat(player)
        kill_stat.deaths += 1
        kill_stat.suicides += 1


class TeamScoreStatsProcessor(StatProcessor):
    def __init__(self, parent):
        StatProcessor.__init__(self, parent)
        self.__last_captured_loc = None

    def process(self, event):
        if type(event) == CapturedLocEvent:
            self.__last_captured_loc = event
            for player in event.player_list:
                self.__process_captured_loc_event(player)

        elif type(event) == RoundWinEvent:
            for player in self.__last_captured_loc.player_list:
                self.__process_round_win_event(player)

        elif type(event) == CapBlockEvent:
            self.__process_cap_block_event(event.player)

    def __process_captured_loc_event(self, player):
        team_score_stat = self._parent.get_team_score_stat(player)
        team_score_stat.flags += 1

    def __process_round_win_event(self, player):
        team_score_stat = self._parent.get_team_score_stat(player)
        team_score_stat.scores += 1

    def __process_cap_block_event(self, player):
        team_score_stat = self._parent.get_team_score_stat(player)
        team_score_stat.blocks += 1


class WeaponStatsProcessor(StatProcessor):
    def __init__(self, parent):
        StatProcessor.__init__(self, parent)
        self.__last_attack = None

    def process(self, event):
        if type(event) == KillEvent:
            self.__process_kill_event(event.player_killer, event.player_killed, event.weapon)
        elif type(event) == SuicideEvent:
            self.__process_suicide_event(event.player, event.weapon)
        elif type(event) == AttackEvent:
            self.__last_attack = event

    def __process_kill_event(self, player_killer, player_killed, weapon):
        weapon_stat = self._parent.get_weapon_stat(player_killer, weapon)

        if player_killer.team != player_killed.team:
            weapon_stat.kills_with_weapon += 1
        else:
            weapon_stat.team_kills += 1

        if self.__last_attack is not None \
                and HitGroupEnum.HEAD.value == self.__last_attack.hit_group \
                and self.__last_attack.player_attacker == player_killer \
                and player_killer.team != player_killed.team:
            weapon_stat.kills_by_head_shot += 1

        weapon_stat = self._parent.get_weapon_stat(player_killed, weapon)
        weapon_stat.deaths_by_weapon += 1

        if player_killer.team == player_killed.team:
            weapon_stat.killed_by_team += 1

        if self.__last_attack is not None \
                and HitGroupEnum.HEAD.value == self.__last_attack.hit_group \
                and self.__last_attack.player_attacked == player_killed:
            weapon_stat.deaths_by_head_shot += 1

    def __process_suicide_event(self, player, weapon):
        weapon_stat = self._parent.get_weapon_stat(player, weapon)
        weapon_stat.suicides += 1


class StreakStatsProcessor(StatProcessor):
    def __init__(self, parent):
        StatProcessor.__init__(self, parent)
        self.__current_streaks = {}

    def process(self, event):
        if type(event) == KillEvent:
            self.__process_kill_event(event.player_killer, event.player_killed)
        elif type(event) == SuicideEvent:
            self.__process_suicide_event(event.player)
        elif type(event) == GameOverEvent:
            self.__process_game_over_event()

    def __process_game_over_event(self):
        for streak in self.__current_streaks.items():
            if streak[1].current_streak >= 1:
                streak_stat = self._parent.get_streak_stat(streak[1].player, streak[1].current_streak)
                streak_stat.times += 1

    def __process_kill_event(self, player_killer, player_killed):
        streak = self.get_current_streak(player_killer)

        if player_killer.team != player_killed.team:
            streak.current_streak += 1

        streak = self.get_current_streak(player_killed)
        streak_stat = self._parent.get_streak_stat(player_killed, streak.current_streak)
        streak_stat.times += 1
        streak.current_streak = 0

    def __process_suicide_event(self, player):
        streak = self.get_current_streak(player)

        streak_stat = self._parent.get_streak_stat(player, streak.current_streak)
        streak_stat.times += 1
        streak.current_streak = 0

    def get_current_streak(self, player):
        current_streak = self.__current_streaks.get(player.id3)

        if current_streak is None:
            current_streak = self.Streak(player)
            self.__current_streaks[player.id3] = current_streak

        return current_streak

    class Streak:
        def __init__(self, player):
            self.player = player
            self.current_streak = 0

        def __str__(self):
            return self.player.id3
