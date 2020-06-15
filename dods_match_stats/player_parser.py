import re


class PlayerParser:

    @staticmethod
    def parse_player_list(players_properties):
        regex = re.compile(r"\(player \"(.+?)\"\)")

        player_properties_list = regex.findall(players_properties)

        player_list = []

        for player_property in player_properties_list:
            player_list.append(PlayerParser.parse_player(player_property))

        return player_list

    @staticmethod
    def parse_player(player_properties):
        regex = re.compile(r"(.+)<(\d+)><(.+)><(.*)>")

        m = regex.search(player_properties)

        name, uid, id3, team = m.groups()

        player_id = 0

        if id3 != "Console" and id3 != "BOT":
            regex = re.compile(r"\d:(.+)]")

            m = regex.search(id3)

            player_id = m.groups()[0]

        return Player(name, uid, id3, player_id, team)


class Player:
    __STEAM_PROFILE_BASE_URL = "http://steamcommunity.com/profiles/"

    def __init__(self, name, uid, id3, player_id, team):
        self.name = name
        self.uid = uid
        self.id3 = id3
        self.id = player_id
        self.team = team
        self.id64 = 76561197960265728 + int(player_id)
        self.profile = Player.__STEAM_PROFILE_BASE_URL + str(self.id64)
        self.current_life = 0

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id3)
