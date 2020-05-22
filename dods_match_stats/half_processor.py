import logging
import time

from dods_match_stats.database_config import get_session, TableMatch


class HalfProcessor:

    def __init__(self, html_writer):
        self.__html_writer = html_writer
        self.__session = get_session()
        self.__first_half_id = None

    def process(self, table_match_id):
        logging.info("[HalfProcessor] - Identifying match as first-half or second-half.")

        if self.__first_half_id is None:
            self.__first_half_id = table_match_id

            logging.info("[HalfProcessor] - Match identified as first-half.")
        else:
            first_half = self.__session.query(TableMatch).get(self.__first_half_id)
            table_match = self.__session.query(TableMatch).get(table_match_id)
            if HalfProcessor.__check_map_name(first_half, table_match):
                if HalfProcessor.__check_time_difference(first_half, table_match):
                    if HalfProcessor.__check_players_equality(first_half, table_match):
                        logging.info("[HalfProcessor] - Match identified as second-half.")

                        self.__html_writer.write(first_half, table_match)
                        self.__first_half_id = None
                    else:
                        logging.info(
                            "[HalfProcessor] - Last half discarded and match identified as first half. "
                            "Reason: players from last match didn't match")
                        self.__first_half_id = table_match_id
                else:
                    logging.info(
                        "[HalfProcessor] - Last half discarded and match identified as first half. "
                        "Reason: time difference exceeds one hour")
                    self.__first_half_id = table_match_id
            else:
                logging.info(
                    "[HalfProcessor] - Last half discarded and match identified as first half. "
                    "Reason: map changed")
                self.__first_half_id = table_match_id

        self.__session.close()

    @staticmethod
    def __check_map_name(first_half, table_match):
        return first_half.map_name == table_match.map_name

    @staticmethod
    def __check_time_difference(first_half, table_match):
        d1_ts = time.mktime(first_half.end_time_stamp.timetuple())
        d2_ts = time.mktime(table_match.start_time_stamp.timetuple())

        difference = int(d2_ts - d1_ts) / 60

        logging.info(
            "[HalfProcessor] - Time difference between halfs is: " + str(difference))

        return difference < 60

    @staticmethod
    def __check_players_equality(first_half, table_match):
        team1_players = set()
        team2_players = set()

        for player in first_half.player_match_list:
            if player.team == "Allies":
                team1_players.add(player.player)
            elif player.team == "Axis":
                team2_players.add(player.player)

        for player in table_match.player_match_list:
            if player.team == "Allies":
                team2_players.add(player.player)
            elif player.team == "Axis":
                team1_players.add(player.player)

        logging.info(
            "[HalfProcessor] - Team1 unique players count: " + str(len(team1_players)))
        logging.info(
            "[HalfProcessor] - Team2 unique players count: " + str(len(team2_players)))

        return 5 <= len(team1_players) <= 8 and 5 <= len(team2_players) <= 8
