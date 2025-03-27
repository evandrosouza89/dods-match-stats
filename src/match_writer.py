import logging
from datetime import datetime

from .database_helper import TableMatch, TablePlayer, TablePlayerMatch, TableAttackEvent, \
    TableKillEvent, TableDominationEvent, TableRevengeEvent, TableConnectionEvent, TableDisconnectionEvent, \
    TableSteamUserIdValidatedEvent, TableEnteredTheGameEvent, TableSuicideEvent, TableJoinedTeamEvent, \
    TableChangedNameEvent, TableSayEvent, TableSayTeamEvent, TableCapBlockEvent, TablePlayerCapturedLoc, \
    TableCapturedLocEvent, TableRoundWinEvent, TableTickScoreEvent, TableADRStat, TableKillStat, \
    TableTeamScoreStat, TableWeaponStat, TableStreakStat, TableChangedRoleEvent
from .team_action_event_parser import TeamEnum


class MatchWriter:

    def __init__(self, database_helper, half_processor, instance_name):
        self.__half_processor = half_processor
        self.__instance_name = instance_name
        self.__db_helper = database_helper
        self.__session = None

    def write(self, match):

        self.__session = self.__db_helper.get_session()

        match_item = None

        try:
            logging.info("[MatchWriter] - Writing match into database.")
            match_item = self.__write_match(match)

            logging.info("[MatchWriter] - Writing player list into database.")
            self.__write_player_list(match, match_item)

            logging.info("[MatchWriter] - Writing events into database.")
            self.__write_events(match, match_item)

            logging.info("[MatchWriter] - Writing stats into database.")
            self.__write_stats(match, match_item)

        except Exception as e:
            logging.exception("[MatchWriter] - Exception occurred: [" + repr(e) + "]")

        logging.info("[MatchWriter] - Writing done.")
        self.__half_processor.process(match_item.id)

        self.__session.close()

    def __write_match(self, match):

        match_item = map_match_to_item(match)

        self.__session.add(match_item)
        self.__session.commit()

        return match_item

    def __write_player_list(self, match, match_item):

        player_match_item_list = []

        for player in match.spectators:
            player_item = self.__session.query(TablePlayer).get(player.id)

            if player_item is None:
                player_item = map_player_to_item(player)
                self.__session.add(player_item)
            else:
                player_item.name = player.name
                self.__session.merge(player_item)

            player_match_item = create_player_match_item(player_item, match_item, TeamEnum.SPECTATOR.value)
            player_match_item_list.append(player_match_item)

        for player in match.team_allies_players:
            player_item = self.__session.query(TablePlayer).get(player.id)

            if player_item is None:
                player_item = map_player_to_item(player)
                self.__session.add(player_item)
            else:
                player_item.name = player.name
                self.__session.merge(player_item)

            player_match_item = create_player_match_item(player_item, match_item, TeamEnum.ALLIES.value)
            player_match_item_list.append(player_match_item)

        for player in match.team_axis_players:
            player_item = self.__session.query(TablePlayer).get(player.id)

            if player_item is None:
                player_item = map_player_to_item(player)
                self.__session.add(player_item)
            else:
                player_item.name = player.name
                self.__session.merge(player_item)

            player_match_item = create_player_match_item(player_item, match_item, TeamEnum.AXIS.value)

            player_match_item_list.append(player_match_item)

        self.__session.commit()

        self.__session.bulk_save_objects(player_match_item_list)

        self.__session.commit()

    def __write_events(self, match, match_item):

        attack_event_item_list = []
        kill_event_item_list = []
        domination_event_item_list = []
        revenge_event_item_list = []
        connection_event_item_list = []
        disconnection_event_item_list = []
        entered_the_game_event_item_list = []
        suiv_event_item_list = []
        suicide_event_item_list = []
        joined_team_event_item_list = []
        changed_role_event_item_list = []
        changed_name_event_item_list = []
        say_event_item_list = []
        say_team_event_item_list = []
        cap_block_event_item_list = []
        captured_loc_players = {}
        player_captured_loc_item_list = []
        round_win_event_item_list = []
        tick_score_event_item_list = []

        for event in match.attack_event_list:
            event_item = map_attack_event_to_item(event, match_item)
            attack_event_item_list.append(event_item)

        for event in match.kill_event_list:
            event_item = map_kill_event_to_item(event, match_item)
            kill_event_item_list.append(event_item)

        for event in match.domination_event_list:
            event_item = map_domination_event_to_item(event, match_item)
            domination_event_item_list.append(event_item)

        for event in match.revenge_event_list:
            event_item = map_revenge_event_to_item(event, match_item)
            revenge_event_item_list.append(event_item)

        for event in match.connection_event_list:
            event_item = map_connection_event_to_item(event, match_item)
            connection_event_item_list.append(event_item)

        for event in match.disconnection_event_list:
            event_item = map_disconnection_event_to_item(event, match_item)
            disconnection_event_item_list.append(event_item)

        for event in match.entered_the_game_event_list:
            event_item = map_entered_the_game_event_to_item(event, match_item)
            entered_the_game_event_item_list.append(event_item)

        for event in match.steam_user_id_validated_event_list:
            event_item = map_steam_user_id_validated_event_to_item(event, match_item)
            suiv_event_item_list.append(event_item)

        for event in match.suicide_event_list:
            event_item = map_suicide_event_to_item(event, match_item)
            suicide_event_item_list.append(event_item)

        for event in match.joined_team_event_list:
            event_item = map_joined_team_event_to_item(event, match_item)
            joined_team_event_item_list.append(event_item)

        for event in match.changed_role_event_list:
            event_item = map_changed_role_event_to_item(event, match_item)
            changed_role_event_item_list.append(event_item)

        for event in match.changed_name_event_list:
            event_item = map_changed_name_event_to_item(event, match_item)
            changed_name_event_item_list.append(event_item)

        for event in match.say_event_list:
            event_item = map_say_event_to_item(event, match_item)
            say_event_item_list.append(event_item)

        for event in match.say_team_event_list:
            event_item = map_say_team_event_to_item(event, match_item)
            say_team_event_item_list.append(event_item)

        for event in match.cap_block_event_list:
            event_item = map_cap_block_event_to_item(event, match_item)
            cap_block_event_item_list.append(event_item)

        for event in match.captured_loc_event_list:
            event_item = map_captured_loc_event_to_item(event, match_item)
            captured_loc_players[event_item] = event.player_list
            self.__session.add(event_item)

        self.__session.commit()

        for event_item in captured_loc_players.keys():
            for player in captured_loc_players[event_item]:
                player_captured_loc_item = create_player_captured_loc_item(player, event_item)
                player_captured_loc_item_list.append(player_captured_loc_item)

        for event in match.round_win_event_list:
            event_item = map_round_win_event_to_item(event, match_item)
            round_win_event_item_list.append(event_item)

        for event in match.tick_score_event_list:
            event_item = map_tick_score_event_to_item(event, match_item)
            tick_score_event_item_list.append(event_item)

        self.__session.bulk_save_objects(attack_event_item_list)
        self.__session.bulk_save_objects(kill_event_item_list)
        self.__session.bulk_save_objects(domination_event_item_list)
        self.__session.bulk_save_objects(revenge_event_item_list)
        self.__session.bulk_save_objects(connection_event_item_list)
        self.__session.bulk_save_objects(disconnection_event_item_list)
        self.__session.bulk_save_objects(entered_the_game_event_item_list)
        self.__session.bulk_save_objects(suiv_event_item_list)
        self.__session.bulk_save_objects(suicide_event_item_list)
        self.__session.bulk_save_objects(joined_team_event_item_list)
        self.__session.bulk_save_objects(changed_role_event_item_list)
        self.__session.bulk_save_objects(changed_name_event_item_list)
        self.__session.bulk_save_objects(say_event_item_list)
        self.__session.bulk_save_objects(say_team_event_item_list)
        self.__session.bulk_save_objects(cap_block_event_item_list)
        self.__session.bulk_save_objects(player_captured_loc_item_list)
        self.__session.bulk_save_objects(round_win_event_item_list)
        self.__session.bulk_save_objects(tick_score_event_item_list)

        self.__session.commit()

    def __write_stats(self, match, match_item):

        adr_stat_item_list = []
        kill_stat_item_list = []
        team_score_stat_item_list = []
        weapon_stat_item_list = []
        streak_stat_item_list = []

        for stat in match.adr_stat_list:
            stat_item = map_adr_stat_to_item(stat, match_item)
            adr_stat_item_list.append(stat_item)

        for stat in match.kill_stat_list:
            stat_item = map_kill_stat_to_item(stat, match_item)
            kill_stat_item_list.append(stat_item)

        for stat in match.team_score_stat_list:
            stat_item = map_team_score_stat_to_item(stat, match_item)
            team_score_stat_item_list.append(stat_item)

        for stat in match.weapon_stat_list:
            stat_item = map_weapon_stat_to_item(stat, match_item)
            weapon_stat_item_list.append(stat_item)

        for stat in match.streak_stat_list:
            stat_item = map_streak_stat_to_item(stat, match_item)
            streak_stat_item_list.append(stat_item)

        self.__session.bulk_save_objects(adr_stat_item_list)
        self.__session.bulk_save_objects(kill_stat_item_list)
        self.__session.bulk_save_objects(team_score_stat_item_list)
        self.__session.bulk_save_objects(weapon_stat_item_list)
        self.__session.bulk_save_objects(streak_stat_item_list)

        self.__session.commit()


def get_datetime_from_string(date_time):
    return datetime.strptime(date_time, '%m/%d/%Y - %H:%M:%S')


def map_match_to_item(match):
    item = TableMatch()

    item.start_time_stamp = get_datetime_from_string(match.start_time_stamp)
    item.end_time_stamp = get_datetime_from_string(match.end_time_stamp)
    item.map_name = match.map_name
    item.team_allies_team_score = match.team_allies_team_score
    item.team_axis_team_score = match.team_axis_team_score
    item.team_allies_tick_score = match.team_allies_tick_score
    item.team_axis_tick_score = match.team_axis_tick_score

    return item


def map_player_to_item(player):
    item = TablePlayer()

    item.id = player.id
    item.name = player.name
    item.id3 = player.id3
    item.team = player.team
    item.profile = player.profile

    return item


def create_player_match_item(player_item, match_item, team):
    item = TablePlayerMatch()

    item.player_id = player_item.id
    item.team = team
    item.match_id = match_item.id

    return item


def setup_event_item(event_item, match_item, time_stamp):
    event_item.match_id = match_item.id
    event_item.time_stamp = get_datetime_from_string(time_stamp)


def map_attack_event_to_item(attack_event, match_item):
    item = TableAttackEvent()

    setup_event_item(item, match_item, attack_event.time_stamp)

    item.player_attacker_id = attack_event.player_attacker.id
    item.player_attacked_id = attack_event.player_attacked.id
    item.weapon = attack_event.weapon
    item.damage = int(attack_event.damage)
    item.health = int(attack_event.health)
    item.hit_group = attack_event.hit_group

    return item


def map_kill_event_to_item(kill_event, match_item):
    item = TableKillEvent()

    setup_event_item(item, match_item, kill_event.time_stamp)

    item.player_killer_id = kill_event.player_killer.id
    item.player_killed_id = kill_event.player_killed.id
    item.weapon = kill_event.weapon

    return item


def map_domination_event_to_item(domination_event, match_item):
    item = TableDominationEvent()

    setup_event_item(item, match_item, domination_event.time_stamp)

    item.player_dominator_id = domination_event.player_dominator.id
    item.player_dominated_id = domination_event.player_dominated.id

    return item


def map_revenge_event_to_item(revenge_event, match_item):
    item = TableRevengeEvent()

    setup_event_item(item, match_item, revenge_event.time_stamp)

    item.player_avenger_id = revenge_event.player_avenger.id
    item.player_killed_id = revenge_event.player_killed.id

    return item


def map_connection_event_to_item(connection_event, match_item):
    item = TableConnectionEvent()

    setup_event_item(item, match_item, connection_event.time_stamp)

    item.player_id = connection_event.player.id
    item.ip_address = connection_event.ip_address

    return item


def map_disconnection_event_to_item(disconnection_event, match_item):
    item = TableDisconnectionEvent()

    setup_event_item(item, match_item, disconnection_event.time_stamp)

    item.player_id = disconnection_event.player.id

    return item


def map_entered_the_game_event_to_item(entered_the_game_event, match_item):
    item = TableEnteredTheGameEvent()

    setup_event_item(item, match_item, entered_the_game_event.time_stamp)

    item.player_id = entered_the_game_event.player.id

    return item


def map_steam_user_id_validated_event_to_item(suiv_event, match_item):
    item = TableSteamUserIdValidatedEvent()

    setup_event_item(item, match_item, suiv_event.time_stamp)

    item.player_id = suiv_event.player.id

    return item


def map_suicide_event_to_item(suicide_event, match_item):
    item = TableSuicideEvent()

    setup_event_item(item, match_item, suicide_event.time_stamp)

    item.player_id = suicide_event.player.id
    item.weapon = suicide_event.weapon

    return item


def map_joined_team_event_to_item(joined_team_event, match_item):
    item = TableJoinedTeamEvent()

    setup_event_item(item, match_item, joined_team_event.time_stamp)

    item.player_id = joined_team_event.player.id
    item.team = joined_team_event.team

    return item


def map_changed_role_event_to_item(changed_role_event, match_item):
    item = TableChangedRoleEvent()

    setup_event_item(item, match_item, changed_role_event.time_stamp)

    item.player_id = changed_role_event.player.id
    item.role = changed_role_event.role

    return item


def map_changed_name_event_to_item(changed_name_event, match_item):
    item = TableChangedNameEvent()

    setup_event_item(item, match_item, changed_name_event.time_stamp)

    item.player_id = changed_name_event.player.id
    item.from_name = changed_name_event.player.name
    item.to_name = changed_name_event.name

    return item


def map_say_event_to_item(say_event, match_item):
    item = TableSayEvent()

    setup_event_item(item, match_item, say_event.time_stamp)

    item.player_id = say_event.player.id
    item.message = say_event.message

    return item


def map_say_team_event_to_item(say_team_event, match_item):
    item = TableSayTeamEvent()

    setup_event_item(item, match_item, say_team_event.time_stamp)

    item.player_id = say_team_event.player.id
    item.message = say_team_event.message

    return item


def map_cap_block_event_to_item(cap_block_event, match_item):
    item = TableCapBlockEvent()

    setup_event_item(item, match_item, cap_block_event.time_stamp)

    item.player_id = cap_block_event.player.id
    item.flag_index = int(cap_block_event.flag_index)
    item.flag_name = cap_block_event.flag_name

    return item


def map_captured_loc_event_to_item(captured_loc_event, match_item):
    item = TableCapturedLocEvent()

    setup_event_item(item, match_item, captured_loc_event.time_stamp)

    item.team = captured_loc_event.team
    item.flag_index = int(captured_loc_event.flag_index)
    item.flag_name = captured_loc_event.flag_name
    item.num_players = int(captured_loc_event.num_players)

    return item


def create_player_captured_loc_item(player, captured_loc_item):
    item = TablePlayerCapturedLoc()

    item.player_id = player.id
    item.captured_loc_id = captured_loc_item.id

    return item


def map_round_win_event_to_item(round_win_event, match_item):
    item = TableRoundWinEvent()

    setup_event_item(item, match_item, round_win_event.time_stamp)

    item.team = round_win_event.team
    item.rounds_won = int(round_win_event.rounds_won)
    item.num_players = int(round_win_event.num_players)

    return item


def map_tick_score_event_to_item(tick_score_event, match_item):
    item = TableTickScoreEvent()

    setup_event_item(item, match_item, tick_score_event.time_stamp)

    item.team = tick_score_event.team
    item.score = int(tick_score_event.score)
    item.total_score = int(tick_score_event.total_score)
    item.num_players = int(tick_score_event.num_players)

    return item


def setup_stat_item(stat_item, match_item, player):
    stat_item.match_id = match_item.id
    stat_item.player_id = player.id


def map_adr_stat_to_item(adr_stat, match_item):
    item = TableADRStat()

    setup_stat_item(item, match_item, adr_stat.player)

    item.enemy_damage = int(adr_stat.enemy_damage)
    item.average_damage = int(adr_stat.average_damage)
    item.team_damage = int(adr_stat.team_damage)
    item.self_damage = int(adr_stat.self_damage)

    return item


def map_kill_stat_to_item(kill_stat, match_item):
    item = TableKillStat()

    setup_stat_item(item, match_item, kill_stat.player)

    item.kills = int(kill_stat.kills)
    item.team_kills = int(kill_stat.team_kills)
    item.deaths = int(kill_stat.deaths)
    item.killed_by_team = int(kill_stat.killed_by_team)
    item.suicides = int(kill_stat.suicides)
    item.kills_by_head_shot = int(kill_stat.kills_by_head_shot)
    item.deaths_by_head_shot = int(kill_stat.deaths_by_head_shot)

    return item


def map_team_score_stat_to_item(team_score_stat, match_item):
    item = TableTeamScoreStat()

    setup_stat_item(item, match_item, team_score_stat.player)

    item.flags = int(team_score_stat.flags)
    item.scores = int(team_score_stat.scores)
    item.blocks = int(team_score_stat.blocks)

    return item


def map_weapon_stat_to_item(weapon_stat, match_item):
    item = TableWeaponStat()

    setup_stat_item(item, match_item, weapon_stat.player)

    item.weapon = weapon_stat.weapon
    item.kills_with_weapon = int(weapon_stat.kills_with_weapon)
    item.deaths_by_weapon = int(weapon_stat.deaths_by_weapon)
    item.team_kills = int(weapon_stat.team_kills)
    item.killed_by_team = int(weapon_stat.killed_by_team)
    item.suicides = int(weapon_stat.suicides)
    item.enemy_damage = int(weapon_stat.enemy_damage)
    item.average_damage = int(weapon_stat.average_damage)
    item.team_damage = int(weapon_stat.team_damage)
    item.kills_by_head_shot = int(weapon_stat.kills_by_head_shot)
    item.deaths_by_head_shot = int(weapon_stat.deaths_by_head_shot)

    return item


def map_streak_stat_to_item(streak_stat, match_item):
    item = TableStreakStat()

    setup_stat_item(item, match_item, streak_stat.player)

    item.players_killed = int(streak_stat.players_killed)
    item.times = int(streak_stat.times)

    return item
