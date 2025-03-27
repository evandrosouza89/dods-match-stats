class Stat(object):
    def __init__(self, match, player):
        self.match = match
        self.player = player


class ADRStat(Stat):
    def __init__(self, match, player):
        Stat.__init__(self, match, player)
        self.player = player
        self.enemy_damage = 0
        self.average_damage = 0
        self.team_damage = 0
        self.self_damage = 0


class KillStat(Stat):
    def __init__(self, match, player):
        Stat.__init__(self, match, player)
        self.player = player
        self.kills = 0
        self.team_kills = 0
        self.deaths = 0
        self.killed_by_team = 0
        self.suicides = 0
        self.kills_by_head_shot = 0
        self.deaths_by_head_shot = 0


class TeamScoreStat(Stat):
    def __init__(self, match, player):
        Stat.__init__(self, match, player)
        self.player = player
        self.flags = 0
        self.scores = 0
        self.blocks = 0


class WeaponStat(Stat):
    def __init__(self, match, player, weapon):
        Stat.__init__(self, match, player)
        self.player = player
        self.weapon = weapon
        self.kills_with_weapon = 0
        self.deaths_by_weapon = 0
        self.team_kills = 0
        self.killed_by_team = 0
        self.suicides = 0
        self.enemy_damage = 0
        self.average_damage = 0
        self.team_damage = 0
        self.kills_by_head_shot = 0
        self.deaths_by_head_shot = 0


class StreakStat(Stat):
    def __init__(self, match, player, players_killed):
        Stat.__init__(self, match, player)
        self.player = player
        self.players_killed = players_killed
        self.times = 0
