import logging
from datetime import datetime

from .database_config import TableMatch, get_base, get_engine, TablePlayer, TablePlayerMatch, TableAttackEvent, \
    TableKillEvent, TableDominationEvent, TableRevengeEvent, TableConnectionEvent, TableDisconnectionEvent, \
    TableSteamUserIdValidatedEvent, TableEnteredTheGameEvent, TableSuicideEvent, TableJoinedTeamEvent, \
    TableChangedNameEvent, TableSayEvent, TableSayTeamEvent, TableCapBlockEvent, TablePlayerCapturedLoc, \
    TableCapturedLocEvent, TableRoundWinEvent, TableTickScoreEvent, TableADRStat, TableKillStat, \
    TableTeamScoreStat, TableWeaponStat, TableStreakStat, TableChangedRoleEvent, commit, query
from .database_config import get_session
from .team_action_event_parser import TeamEnum


class MatchWriter:

    def __init__(self, half_processor):
        self.__half_processor = half_processor
        self.__session = get_session()
        get_base().metadata.create_all(get_engine())

    def write(self, match):
        table_match = self.__write_match(match)

        logging.info("[MatchWriter] - Writing player list.")
        self.__write_player_list(match, table_match)
        logging.info("[MatchWriter] - Writing events.")
        self.__write_events(match, table_match)

        logging.info("[MatchWriter] - Writing stats.")
        self.__write_stats(match, table_match)

        logging.info("[MatchWriter] - Writing done.")
        self.__half_processor.process(table_match.id)

        self.__session.close()

    def __write_match(self, match):
        table_match = map_match_to_table(match)

        self.__session.add(table_match)
        commit()

        return table_match

    def __write_player_list(self, match, table_match):
        __table_player_match_list = []

        for player in match.spectators:
            table_player = query(TablePlayer, player.id)

            if table_player is None:
                table_player = map_player_to_table(player)
                self.__session.add(table_player)
            else:
                table_player.name = player.name
                self.__session.merge(table_player)

            table_player_match = create_player_match_entry(table_player, table_match, TeamEnum.SPECTATOR.value)
            __table_player_match_list.append(table_player_match)

        for player in match.team_allies_players:
            table_player = query(TablePlayer, player.id)

            if table_player is None:
                table_player = map_player_to_table(player)
                self.__session.add(table_player)
            else:
                table_player.name = player.name
                self.__session.merge(table_player)

            table_player_match = create_player_match_entry(table_player, table_match, TeamEnum.ALLIES.value)
            __table_player_match_list.append(table_player_match)

        for player in match.team_axis_players:
            table_player = query(TablePlayer, player.id)

            if table_player is None:
                table_player = map_player_to_table(player)
                self.__session.add(table_player)
            else:
                table_player.name = player.name
                self.__session.merge(table_player)

            table_player_match = create_player_match_entry(table_player, table_match, TeamEnum.AXIS.value)

            __table_player_match_list.append(table_player_match)

        commit()

        self.__session.bulk_save_objects(__table_player_match_list)

        commit()

    def __write_events(self, match, table_match):
        __table_attack_event_list = []
        __table_kill_event_list = []
        __table_domination_event_list = []
        __table_revenge_event_list = []
        __table_connection_event_list = []
        __table_disconnection_event_list = []
        __table_entered_the_game_event_list = []
        __table_suiv_event_list = []
        __table_suicide_event_list = []
        __table_joined_team_event_list = []
        __table_changed_role_event_list = []
        __table_changed_name_event_list = []
        __table_say_event_list = []
        __table_say_team_event_list = []
        __table_cap_block_event_list = []
        __captured_loc_players = {}
        __table_player_captured_loc_list = []
        __table_round_win_event_list = []
        __table_tick_score_event_list = []

        for event in match.attack_event_list:
            table_event = map_attack_event_to_table(event, table_match)
            __table_attack_event_list.append(table_event)

        for event in match.kill_event_list:
            table_event = map_kill_event_to_table(event, table_match)
            __table_kill_event_list.append(table_event)

        for event in match.domination_event_list:
            table_event = map_domination_event_to_table(event, table_match)
            __table_domination_event_list.append(table_event)

        for event in match.revenge_event_list:
            table_event = map_revenge_event_to_table(event, table_match)
            __table_revenge_event_list.append(table_event)

        for event in match.connection_event_list:
            table_event = map_connection_event_to_table(event, table_match)
            __table_connection_event_list.append(table_event)

        for event in match.disconnection_event_list:
            table_event = map_disconnection_event_to_table(event, table_match)
            __table_disconnection_event_list.append(table_event)

        for event in match.entered_the_game_event_list:
            table_event = map_entered_the_game_event_to_table(event, table_match)
            __table_entered_the_game_event_list.append(table_event)

        for event in match.steam_user_id_validated_event_list:
            table_event = map_steam_user_id_validated_event_to_table(event, table_match)
            __table_suiv_event_list.append(table_event)

        for event in match.suicide_event_list:
            table_event = map_suicide_event_to_table(event, table_match)
            __table_suicide_event_list.append(table_event)

        for event in match.joined_team_event_list:
            table_event = map_joined_team_event_to_table(event, table_match)
            __table_joined_team_event_list.append(table_event)

        for event in match.changed_role_event_list:
            table_event = map_changed_role_event_to_table(event, table_match)
            __table_changed_role_event_list.append(table_event)

        for event in match.changed_name_event_list:
            table_event = map_changed_name_event_to_table(event, table_match)
            __table_changed_name_event_list.append(table_event)

        for event in match.say_event_list:
            table_event = map_say_event_to_table(event, table_match)
            __table_say_event_list.append(table_event)

        for event in match.say_team_event_list:
            table_event = map_say_team_event_to_table(event, table_match)
            __table_say_team_event_list.append(table_event)

        for event in match.cap_block_event_list:
            table_event = map_cap_block_event_to_table(event, table_match)
            __table_cap_block_event_list.append(table_event)

        for event in match.captured_loc_event_list:
            table_event = map_captured_loc_event_to_table(event, table_match)
            __captured_loc_players[table_event] = event.player_list
            self.__session.add(table_event)

        commit()

        for table_event in __captured_loc_players.keys():
            for player in __captured_loc_players[table_event]:
                table_player_captured_loc = create_player_captured_loc_entry(player, table_event)
                __table_player_captured_loc_list.append(table_player_captured_loc)

        for event in match.round_win_event_list:
            table_event = map_round_win_event_to_table(event, table_match)
            __table_round_win_event_list.append(table_event)

        for event in match.tick_score_event_list:
            table_event = map_tick_score_event_to_table(event, table_match)
            __table_tick_score_event_list.append(table_event)

        self.__session.bulk_save_objects(__table_attack_event_list)
        self.__session.bulk_save_objects(__table_kill_event_list)
        self.__session.bulk_save_objects(__table_domination_event_list)
        self.__session.bulk_save_objects(__table_revenge_event_list)
        self.__session.bulk_save_objects(__table_connection_event_list)
        self.__session.bulk_save_objects(__table_disconnection_event_list)
        self.__session.bulk_save_objects(__table_entered_the_game_event_list)
        self.__session.bulk_save_objects(__table_suiv_event_list)
        self.__session.bulk_save_objects(__table_suicide_event_list)
        self.__session.bulk_save_objects(__table_joined_team_event_list)
        self.__session.bulk_save_objects(__table_changed_role_event_list)
        self.__session.bulk_save_objects(__table_changed_name_event_list)
        self.__session.bulk_save_objects(__table_say_event_list)
        self.__session.bulk_save_objects(__table_say_team_event_list)
        self.__session.bulk_save_objects(__table_cap_block_event_list)
        self.__session.bulk_save_objects(__table_player_captured_loc_list)
        self.__session.bulk_save_objects(__table_round_win_event_list)
        self.__session.bulk_save_objects(__table_tick_score_event_list)

        commit()

    def __write_stats(self, match, table_match):
        __table_adr_stat_list = []
        __table_kill_stat_list = []
        __table_team_score_stat_list = []
        __table_weapon_stat_list = []
        __table_streak_stat_list = []

        for stat in match.adr_stat_list:
            table_stat = map_adr_stat_to_table(stat, table_match)
            __table_adr_stat_list.append(table_stat)

        for stat in match.kill_stat_list:
            table_stat = map_kill_stat_to_table(stat, table_match)
            __table_kill_stat_list.append(table_stat)

        for stat in match.team_score_stat_list:
            table_stat = map_team_score_stat_to_table(stat, table_match)
            __table_team_score_stat_list.append(table_stat)

        for stat in match.weapon_stat_list:
            table_stat = map_weapon_stat_to_table(stat, table_match)
            __table_weapon_stat_list.append(table_stat)

        for stat in match.streak_stat_list:
            table_stat = map_streak_stat_to_table(stat, table_match)
            __table_streak_stat_list.append(table_stat)

        self.__session.bulk_save_objects(__table_adr_stat_list)
        self.__session.bulk_save_objects(__table_kill_stat_list)
        self.__session.bulk_save_objects(__table_team_score_stat_list)
        self.__session.bulk_save_objects(__table_weapon_stat_list)
        self.__session.bulk_save_objects(__table_streak_stat_list)

        commit()


def get_datetime_from_string(date_time):
    return datetime.strptime(date_time, '%m/%d/%Y - %H:%M:%S')


def map_match_to_table(match):
    table_match = TableMatch()

    table_match.start_time_stamp = get_datetime_from_string(match.start_time_stamp)
    table_match.end_time_stamp = get_datetime_from_string(match.end_time_stamp)
    table_match.map_name = match.map_name
    table_match.team_allies_team_score = match.team_allies_team_score
    table_match.team_axis_team_score = match.team_axis_team_score
    table_match.team_allies_tick_score = match.team_allies_tick_score
    table_match.team_axis_tick_score = match.team_axis_tick_score

    return table_match


def map_player_to_table(player):
    table_player = TablePlayer()
    table_player.id = player.id
    table_player.name = player.name
    table_player.id3 = player.id3
    table_player.team = player.team
    table_player.profile = player.profile

    return table_player


def create_player_match_entry(table_player, table_match, team):
    table_player_match = TablePlayerMatch()

    table_player_match.player_id = table_player.id
    table_player_match.team = team
    table_player_match.match_id = table_match.id

    return table_player_match


def create_table_event(table_event, table_match, time_stamp):
    table_event.match_id = table_match.id
    table_event.time_stamp = get_datetime_from_string(time_stamp)


def map_attack_event_to_table(attack_event, table_match):
    table_attack_event = TableAttackEvent()

    create_table_event(table_attack_event, table_match, attack_event.time_stamp)

    table_attack_event.player_attacker_id = attack_event.player_attacker.id
    table_attack_event.player_attacked_id = attack_event.player_attacked.id
    table_attack_event.weapon = attack_event.weapon
    table_attack_event.damage = int(attack_event.damage)
    table_attack_event.health = int(attack_event.health)
    table_attack_event.hit_group = attack_event.hit_group

    return table_attack_event


def map_kill_event_to_table(kill_event, table_match):
    table = TableKillEvent()

    create_table_event(table, table_match, kill_event.time_stamp)

    table.player_killer_id = kill_event.player_killer.id
    table.player_killed_id = kill_event.player_killed.id
    table.weapon = kill_event.weapon

    return table


def map_domination_event_to_table(domination_event, table_match):
    table = TableDominationEvent()

    create_table_event(table, table_match, domination_event.time_stamp)

    table.player_dominator_id = domination_event.player_dominator.id
    table.player_dominated_id = domination_event.player_dominated.id

    return table


def map_revenge_event_to_table(revenge_event, table_match):
    table = TableRevengeEvent()

    create_table_event(table, table_match, revenge_event.time_stamp)

    table.player_avenger_id = revenge_event.player_avenger.id
    table.player_killed_id = revenge_event.player_killed.id

    return table


def map_connection_event_to_table(connection_event, table_match):
    table = TableConnectionEvent()

    create_table_event(table, table_match, connection_event.time_stamp)

    table.player_id = connection_event.player.id
    table.ip_address = connection_event.ip_address

    return table


def map_disconnection_event_to_table(disconnection_event, table_match):
    table = TableDisconnectionEvent()

    create_table_event(table, table_match, disconnection_event.time_stamp)

    table.player_id = disconnection_event.player.id

    return table


def map_entered_the_game_event_to_table(entered_the_game_event, table_match):
    table = TableEnteredTheGameEvent()

    create_table_event(table, table_match, entered_the_game_event.time_stamp)

    table.player_id = entered_the_game_event.player.id

    return table


def map_steam_user_id_validated_event_to_table(suiv_event, table_match):
    table = TableSteamUserIdValidatedEvent()

    create_table_event(table, table_match, suiv_event.time_stamp)

    table.player_id = suiv_event.player.id

    return table


def map_suicide_event_to_table(suicide_event, table_match):
    table = TableSuicideEvent()

    create_table_event(table, table_match, suicide_event.time_stamp)

    table.player_id = suicide_event.player.id
    table.weapon = suicide_event.weapon

    return table


def map_joined_team_event_to_table(joined_team_event, table_match):
    table = TableJoinedTeamEvent()

    create_table_event(table, table_match, joined_team_event.time_stamp)

    table.player_id = joined_team_event.player.id
    table.team = joined_team_event.team

    return table


def map_changed_role_event_to_table(changed_role_event, table_match):
    table = TableChangedRoleEvent()

    create_table_event(table, table_match, changed_role_event.time_stamp)

    table.player_id = changed_role_event.player.id
    table.role = changed_role_event.role

    return table


def map_changed_name_event_to_table(changed_name_event, table_match):
    table = TableChangedNameEvent()

    create_table_event(table, table_match, changed_name_event.time_stamp)

    table.player_id = changed_name_event.player.id
    table.from_name = changed_name_event.player.name
    table.to_name = changed_name_event.name

    return table


def map_say_event_to_table(say_event, table_match):
    table = TableSayEvent()

    create_table_event(table, table_match, say_event.time_stamp)

    table.player_id = say_event.player.id
    table.message = say_event.message

    return table


def map_say_team_event_to_table(say_team_event, table_match):
    table = TableSayTeamEvent()

    create_table_event(table, table_match, say_team_event.time_stamp)

    table.player_id = say_team_event.player.id
    table.message = say_team_event.message

    return table


def map_cap_block_event_to_table(cap_block_event, table_match):
    table = TableCapBlockEvent()

    create_table_event(table, table_match, cap_block_event.time_stamp)

    table.player_id = cap_block_event.player.id
    table.flag_index = int(cap_block_event.flag_index)
    table.flag_name = cap_block_event.flag_name

    return table


def map_captured_loc_event_to_table(captured_loc_event, table_match):
    table = TableCapturedLocEvent()

    create_table_event(table, table_match, captured_loc_event.time_stamp)

    table.team = captured_loc_event.team
    table.flag_index = int(captured_loc_event.flag_index)
    table.flag_name = captured_loc_event.flag_name
    table.num_players = int(captured_loc_event.num_players)

    return table


def create_player_captured_loc_entry(player, table_captured_loc):
    table_player_captured_loc = TablePlayerCapturedLoc()

    table_player_captured_loc.player_id = player.id
    table_player_captured_loc.captured_loc_id = table_captured_loc.id

    return table_player_captured_loc


def map_round_win_event_to_table(round_win_event, table_match):
    table = TableRoundWinEvent()

    create_table_event(table, table_match, round_win_event.time_stamp)

    table.team = round_win_event.team
    table.rounds_won = int(round_win_event.rounds_won)
    table.num_players = int(round_win_event.num_players)

    return table


def map_tick_score_event_to_table(tick_score_event, table_match):
    table = TableTickScoreEvent()

    create_table_event(table, table_match, tick_score_event.time_stamp)

    table.team = tick_score_event.team
    table.score = int(tick_score_event.score)
    table.total_score = int(tick_score_event.total_score)
    table.num_players = int(tick_score_event.num_players)

    return table


def create_table_stat(table_stat, table_match, player):
    table_stat.match_id = table_match.id
    table_stat.player_id = player.id


def map_adr_stat_to_table(adr_stat, table_match):
    table = TableADRStat()

    create_table_stat(table, table_match, adr_stat.player)
    table.enemy_damage = int(adr_stat.enemy_damage)
    table.average_damage = int(adr_stat.average_damage)
    table.team_damage = int(adr_stat.team_damage)

    return table


def map_kill_stat_to_table(kill_stat, table_match):
    table = TableKillStat()

    create_table_stat(table, table_match, kill_stat.player)
    table.kills = int(kill_stat.kills)
    table.team_kills = int(kill_stat.team_kills)
    table.deaths = int(kill_stat.deaths)
    table.killed_by_team = int(kill_stat.killed_by_team)
    table.suicides = int(kill_stat.suicides)
    table.kills_by_head_shot = int(kill_stat.kills_by_head_shot)
    table.deaths_by_head_shot = int(kill_stat.deaths_by_head_shot)

    return table


def map_team_score_stat_to_table(team_score_stat, table_match):
    table = TableTeamScoreStat()

    create_table_stat(table, table_match, team_score_stat.player)
    table.flags = int(team_score_stat.flags)
    table.scores = int(team_score_stat.scores)
    table.blocks = int(team_score_stat.blocks)

    return table


def map_weapon_stat_to_table(weapon_stat, table_match):
    table = TableWeaponStat()

    create_table_stat(table, table_match, weapon_stat.player)
    table.weapon = weapon_stat.weapon
    table.kills_with_weapon = int(weapon_stat.kills_with_weapon)
    table.deaths_by_weapon = int(weapon_stat.deaths_by_weapon)
    table.team_kills = int(weapon_stat.team_kills)
    table.killed_by_team = int(weapon_stat.killed_by_team)
    table.suicides = int(weapon_stat.suicides)
    table.enemy_damage = int(weapon_stat.enemy_damage)
    table.average_damage = int(weapon_stat.average_damage)
    table.team_damage = int(weapon_stat.team_damage)
    table.kills_by_head_shot = int(weapon_stat.kills_by_head_shot)
    table.deaths_by_head_shot = int(weapon_stat.deaths_by_head_shot)

    return table


def map_streak_stat_to_table(streak_stat, table_match):
    table = TableStreakStat()

    create_table_stat(table, table_match, streak_stat.player)
    table.players_killed = int(streak_stat.players_killed)
    table.times = int(streak_stat.times)

    return table
