import io
import logging
import os
import sys

from yattag import Doc

from . import styles
from .utils import Utils


class HtmlWriter:

    def __init__(self, output_dir):
        self.__output_dir = output_dir

        if not Utils.test_file_creation(output_dir):
            logging.error(
                "[HtmlWriter] - Unable to write to the OUTPUT_DIR: " + output_dir + ". Verify the folder permissions.")

            sys.exit(2)

    def write(self, table_match_half1, table_match_half2):

        logging.info(
            "[HtmlWriter] - Writing " + str(table_match_half1.id)
            + "_" + str(table_match_half2.id) + "@" + table_match_half1.map_name)

        map_name = table_match_half1.map_name

        team1_total_score = table_match_half1.team_allies_team_score + table_match_half2.team_axis_team_score
        team2_total_score = table_match_half1.team_axis_team_score + table_match_half2.team_allies_team_score

        team1_tick_score = table_match_half1.team_allies_tick_score + table_match_half2.team_axis_tick_score
        team2_tick_score = table_match_half1.team_axis_tick_score + table_match_half2.team_allies_tick_score

        spectators = set()
        team1_players = set()
        team2_players = set()

        for player in table_match_half1.player_match_list:
            if player.team == "Spectator":
                spectators.add(player.player)
            elif player.team == "Allies":
                team1_players.add(player.player)
            elif player.team == "Axis":
                team2_players.add(player.player)

        for player in table_match_half2.player_match_list:
            if player.team == "Spectator":
                spectators.add(player.player)
            elif player.team == "Allies":
                team2_players.add(player.player)
            elif player.team == "Axis":
                team1_players.add(player.player)

        file_name = Utils.generate_file_name(table_match_half1, table_match_half2)

        HtmlWriter._write_html(self.__output_dir,
                               file_name,
                               map_name,
                               table_match_half1,
                               table_match_half2,
                               spectators,
                               team1_players,
                               team2_players,
                               team1_total_score,
                               team2_total_score,
                               team1_tick_score,
                               team2_tick_score)

        logging.info(
            "[HtmlWriter] - Writing " + file_name + " done")

    @staticmethod
    def _write_html(output_dir,
                    file_name,
                    map_name,
                    match_half1,
                    match_half2,
                    spectators,
                    team1_players,
                    team2_players,
                    team1_total_score,
                    team2_total_score,
                    team1_tick_score,
                    team2_tick_score):

        doc, tag, text = Doc().tagtext()

        with tag("html"):
            with tag("head"):
                with tag("style"):
                    doc.asis(styles)

            with tag("body"):
                with tag("center"):
                    with tag("div"):
                        doc.attr(klass="teamsBox")
                        HtmlWriter._get_teams_content(doc, tag, text, map_name,
                                                      HtmlWriter._custom_strftime('{S} of %B %Y',
                                                                                  match_half1.start_time_stamp),
                                                      match_half1.start_time_stamp,
                                                      [team1_total_score, team2_total_score],
                                                      [team1_tick_score, team2_tick_score])

                    with tag("div"):
                        HtmlWriter._get_troop_report_separator(doc, tag, text, "TEAM 1 WAR REPORT")

                        HtmlWriter._get_stats_content(doc, tag, text, "Soldier name", team1_players,
                                                      match_half1.kill_stat_list + match_half2.kill_stat_list,
                                                      match_half1.adr_stat_list + match_half2.adr_stat_list,
                                                      match_half1.team_score_stat_list + match_half2.team_score_stat_list,
                                                      match_half1.streak_stat_list + match_half2.streak_stat_list)

                        HtmlWriter._get_troop_report_separator(doc, tag, text, "TEAM 2 WAR REPORT")

                        HtmlWriter._get_stats_content(doc, tag, text, "Soldier name", team2_players,
                                                      match_half1.kill_stat_list + match_half2.kill_stat_list,
                                                      match_half1.adr_stat_list + match_half2.adr_stat_list,
                                                      match_half1.team_score_stat_list + match_half2.team_score_stat_list,
                                                      match_half1.streak_stat_list + match_half2.streak_stat_list)

        if not output_dir.endswith(os.sep):
            output_dir += os.sep

        f = io.open(output_dir + file_name + ".html", "w", encoding="utf-8")
        f.write(doc.getvalue())
        f.close()

    @staticmethod
    def _get_date_day_suffix(d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

    @staticmethod
    def _custom_strftime(fmt, t):
        return t.strftime(fmt).replace('{S}', str(t.day) + HtmlWriter._get_date_day_suffix(t.day))

    @staticmethod
    def _get_teams_content(doc, tag, text, map_name, match_date, start_time_stamp, scores, tick_scores):
        with tag("div"):
            doc.attr(klass="team")
            with tag("div"):
                doc.attr(klass="teamName")
                text("Team 1")
            with tag("div"):
                doc.attr(klass="score")
                text(scores[0])
            with tag("div"):
                text("+" + str(tick_scores[0]) + " ticks")
        with tag("div"):
            with tag("div"):
                doc.attr(klass="hour")

                if start_time_stamp.hour < 10:
                    time = "0" + str(start_time_stamp.hour)
                else:
                    time = str(start_time_stamp.hour)

                if start_time_stamp.minute < 10:
                    time += "0" + str(start_time_stamp.minute)
                else:
                    time += str(start_time_stamp.minute)

                text(time)
            with tag("div"):
                doc.attr(klass="day")
                text(match_date)
            with tag("div"):
                text("Match Over")
            with tag("div"):
                doc.asis('&nbsp;')
            with tag("div"):
                doc.attr(klass="mapName")
                text(map_name)
        with tag("div"):
            doc.attr(klass="team")
            with tag("div"):
                doc.attr(klass="teamName")
                text("Team 2")
            with tag("div"):
                doc.attr(klass="score")
                text(scores[1])
            with tag("div"):
                text("+" + str(tick_scores[1]) + " ticks")

    @staticmethod
    def _get_stats_content(doc, tag, text, team, player_list, kill_stat_list, adr_stat_list, team_score_stat_list,
                           streak_stat_list):
        with tag("table"):
            with tag("thead"):
                with tag("tr"):
                    with tag("th"):
                        doc.asis(team)
                    with tag("th"):
                        text("K-D")
                    with tag("th"):
                        text("+-")
                    with tag("th"):
                        text("Team Kills")
                    with tag("th"):
                        text("Suicides")
                    with tag("th"):
                        text("Enemy Damage")
                    with tag("th"):
                        text("Average Damage")
                    with tag("th"):
                        text("Team Damage")
                    with tag("th"):
                        text("HS%")
                    with tag("th"):
                        text("Scores")
                    with tag("th"):
                        text("Flags")
                    with tag("th"):
                        text("Blocks")
                    with tag("th"):
                        text("Multi-kill streaks")
            with tag("tbody"):
                for player in player_list:
                    found_kill_stat_list = (kill_stat for kill_stat in kill_stat_list if
                                            kill_stat.player_id == player.id)
                    found_adr_stat_list = (adr_stat for adr_stat in adr_stat_list if adr_stat.player_id == player.id)
                    found_team_score_stat_list = (team_score_stat for team_score_stat in team_score_stat_list if
                                                  team_score_stat.player_id == player.id)
                    found_streak_stat_list = (streak_stat for streak_stat in streak_stat_list if
                                              streak_stat.player_id == player.id)

                    found_streak_stat_dict = {}
                    for key in found_streak_stat_list:
                        if key.players_killed in found_streak_stat_dict:
                            found_streak_stat_dict[key.players_killed] = found_streak_stat_dict[
                                                                             key.players_killed] + key.times
                        else:
                            found_streak_stat_dict[key.players_killed] = key.times

                    k = 0
                    d = 0
                    tk = 0
                    s = 0
                    ed = 0
                    ad = 0
                    td = 0
                    hs = 0
                    sc = 0
                    f = 0
                    b = 0
                    streaks = ""

                    for kill_stat in found_kill_stat_list:
                        k += kill_stat.kills
                        d += kill_stat.deaths
                        tk += kill_stat.team_kills
                        s += kill_stat.suicides
                        hs += kill_stat.kills_by_head_shot
                    for adr_stat in found_adr_stat_list:
                        ed += adr_stat.enemy_damage
                        ad += int(adr_stat.average_damage / 2)
                        td += adr_stat.team_damage
                    for team_score_stat in found_team_score_stat_list:
                        sc += team_score_stat.scores
                        f += team_score_stat.flags
                        b += team_score_stat.blocks
                    for key in sorted(found_streak_stat_dict, reverse=True):
                        streaks += str(key) + "K(" + str(found_streak_stat_dict[key]) + "x) "
                    with tag("tr"):
                        with tag("td"):
                            doc.attr(klass="playerNames")
                            with tag('a', href=player.profile):
                                doc.asis(player.name)
                        with tag("td"):
                            text(str(k) + "-" + str(d))
                        with tag("td"):
                            text(k - d)
                        with tag("td"):
                            text(tk)
                        with tag("td"):
                            text(s)
                        with tag("td"):
                            text(ed)
                        with tag("td"):
                            text(ad)
                        with tag("td"):
                            text(td)
                        with tag("td"):
                            if k > 0:
                                text(int(round((hs / k) * 100)))
                            else:
                                text("0")
                        with tag("td"):
                            text(sc)
                        with tag("td"):
                            text(f)
                        with tag("td"):
                            text(b)
                        with tag("td"):
                            doc.attr(klass="streaks")
                            text(streaks)

    @staticmethod
    def _get_troop_report_separator(doc, tag, text, team_name):
        with tag("div"):
            doc.attr(klass="reportSeparator")
            with tag("div"):
                text(
                    "== == == == == == == == == == == == == == == == == == == == == == == == "
                    "== == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==")
            with tag("div"):
                text(team_name)
            with tag("div"):
                text(
                    "== == == == == == == == == == == == == == == == == == == == == == == == "
                    "== == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==")
