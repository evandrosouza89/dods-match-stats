from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, SmallInteger, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

from . import config

__Base = declarative_base()
__engine = create_engine("mysql+pymysql://" + config.get("DatabaseSection", "database.user")
                         + ":" + config.get("DatabaseSection", "database.password")
                         + "@" + config.get("DatabaseSection", "database.url")
                         + "/" + config.get("DatabaseSection", "database.schema")
                         + "?charset=utf8",
                         echo=False, pool_recycle=10, encoding="utf-8")

__Session = sessionmaker(bind=__engine)
__session = __Session()


def get_base():
    return __Base


def get_session():
    return __session


def get_engine():
    return __engine


class TableStreakStat(__Base):
    __tablename__ = "streak_stat"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    players_killed = Column(SmallInteger, nullable=False)
    times = Column(SmallInteger, nullable=False)


class TableWeaponStat(__Base):
    __tablename__ = "weapon_stat"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    weapon = Column(String(32), nullable=False)
    kills_with_weapon = Column(SmallInteger, nullable=False)
    deaths_by_weapon = Column(SmallInteger, nullable=False)
    team_kills = Column(SmallInteger, nullable=False)
    killed_by_team = Column(SmallInteger, nullable=False)
    suicides = Column(SmallInteger, nullable=False)
    enemy_damage = Column(Integer, nullable=False)
    average_damage = Column(Integer, nullable=False)
    team_damage = Column(Integer, nullable=False)
    kills_by_head_shot = Column(SmallInteger, nullable=False)
    deaths_by_head_shot = Column(SmallInteger, nullable=False)


class TableTeamScoreStat(__Base):
    __tablename__ = "team_score_stat"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    flags = Column(SmallInteger, nullable=False)
    scores = Column(SmallInteger, nullable=False)
    blocks = Column(SmallInteger, nullable=False)


class TableKillStat(__Base):
    __tablename__ = "kill_stat"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    kills = Column(SmallInteger, nullable=False)
    team_kills = Column(SmallInteger, nullable=False)
    deaths = Column(SmallInteger, nullable=False)
    killed_by_team = Column(SmallInteger, nullable=False)
    suicides = Column(SmallInteger, nullable=False)
    kills_by_head_shot = Column(SmallInteger, nullable=False)
    deaths_by_head_shot = Column(SmallInteger, nullable=False)


class TableADRStat(__Base):
    __tablename__ = "adr_stat"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    enemy_damage = Column(Integer, nullable=False)
    average_damage = Column(Integer, nullable=False)
    team_damage = Column(Integer, nullable=False)


class TableTickScoreEvent(__Base):
    __tablename__ = "tick_score_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    team = Column(String(16), nullable=False)
    score = Column(SmallInteger, nullable=False)
    total_score = Column(SmallInteger, nullable=False)
    num_players = Column(SmallInteger, nullable=False)


class TableRoundWinEvent(__Base):
    __tablename__ = "round_win_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    team = Column(String(16), nullable=False)
    rounds_won = Column(SmallInteger, nullable=False)
    num_players = Column(SmallInteger, nullable=False)


class TablePlayerCapturedLoc(__Base):
    __tablename__ = "player_captured_loc"

    id = Column(Integer, primary_key=True, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    captured_loc_id = Column(Integer, ForeignKey("captured_loc_event.id"), nullable=False)
    captured_loc = relationship("TableCapturedLocEvent", foreign_keys=captured_loc_id)


class TableCapturedLocEvent(__Base):
    __tablename__ = "captured_loc_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    team = Column(String(16), nullable=False)
    flag_index = Column(SmallInteger, nullable=False)
    flag_name = Column(String(64), nullable=False)
    num_players = Column(SmallInteger, nullable=False)


class TableCapBlockEvent(__Base):
    __tablename__ = "cap_block_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    flag_index = Column(SmallInteger, nullable=False)
    flag_name = Column(String(64), nullable=False)


class TableSayTeamEvent(__Base):
    __tablename__ = "say_team_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    message = Column(Text, nullable=False)


class TableSayEvent(__Base):
    __tablename__ = "say_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    message = Column(Text, nullable=False)


class TableChangedNameEvent(__Base):
    __tablename__ = "changed_name_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    from_name = Column(String(128), nullable=False)
    to_name = Column(String(128), nullable=False)


class TableChangedRoleEvent(__Base):
    __tablename__ = "changed_role_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    role = Column(String(32), nullable=False)


class TableJoinedTeamEvent(__Base):
    __tablename__ = "joined_team_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    team = Column(String(16), nullable=False)


class TableSuicideEvent(__Base):
    __tablename__ = "suicide_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    weapon = Column(String(32), nullable=False)


class TableSteamUserIdValidatedEvent(__Base):
    __tablename__ = "steam_user_id_validated_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)


class TableEnteredTheGameEvent(__Base):
    __tablename__ = "entered_the_game_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)


class TableDisconnectionEvent(__Base):
    __tablename__ = "disconnection_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)


class TableConnectionEvent(__Base):
    __tablename__ = "connection_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    ip_address = Column(String(128), nullable=False)


class TableRevengeEvent(__Base):
    __tablename__ = "revenge_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_avenger_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player_avenger = relationship("TablePlayer", foreign_keys=player_avenger_id)
    player_killed_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player_killed = relationship("TablePlayer", foreign_keys=player_killed_id)


class TableDominationEvent(__Base):
    __tablename__ = "domination_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_dominator_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player_dominator = relationship("TablePlayer", foreign_keys=player_dominator_id)
    player_dominated_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player_dominated = relationship("TablePlayer", foreign_keys=player_dominated_id)


class TableKillEvent(__Base):
    __tablename__ = "kill_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_killer_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player_killer = relationship("TablePlayer", foreign_keys=player_killer_id)
    player_killed_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player_killed = relationship("TablePlayer", foreign_keys=player_killed_id)
    weapon = Column(String(32), nullable=False)


class TableAttackEvent(__Base):
    __tablename__ = "attack_event"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    time_stamp = Column(DateTime, nullable=False)
    player_attacker_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player_attacker = relationship("TablePlayer", foreign_keys=player_attacker_id)
    player_attacked_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player_attacked = relationship("TablePlayer", foreign_keys=player_attacked_id)
    weapon = Column(String(32), nullable=False)
    damage = Column(SmallInteger, nullable=False)
    health = Column(SmallInteger, nullable=False)
    hit_group = Column(String(16), nullable=False)


class TablePlayerMatch(__Base):
    __tablename__ = "player_match"

    id = Column(Integer, primary_key=True, nullable=False)
    match_id = Column(Integer, ForeignKey("match.id"), nullable=False)
    match = relationship("TableMatch", foreign_keys=match_id)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("TablePlayer", foreign_keys=player_id)
    team = Column(String(16), nullable=False)


class TablePlayer(__Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(128), nullable=False)
    id3 = Column(String(16), nullable=False)
    profile = Column(String(128), nullable=False)


class TableMatch(__Base):
    __tablename__ = "match"

    id = Column(Integer, primary_key=True, nullable=False)
    start_time_stamp = Column(DateTime, nullable=False)
    end_time_stamp = Column(DateTime, nullable=False)
    map_name = Column(String(32), nullable=False)
    team_allies_team_score = Column(SmallInteger, nullable=False)
    team_axis_team_score = Column(SmallInteger, nullable=False)
    team_allies_tick_score = Column(SmallInteger, nullable=False)
    team_axis_tick_score = Column(SmallInteger, nullable=False)
