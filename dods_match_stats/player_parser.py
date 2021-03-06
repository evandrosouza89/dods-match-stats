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

        if id3 != "Console" and id3 != "BOT":
            regex = re.compile(r"\d:(.+)]")

            m = regex.search(id3)

            player_id = m.groups()[0]

        else:
            player_id = 1
            name = "TV"

        return Player(name, uid, id3, player_id, team)


class Player:
    __STEAM_PROFILE_BASE_URL = "http://steamcommunity.com/profiles/"

    def __init__(self, name, uid, id3, player_id, team):
        self.name = name
        self.uid = uid
        self.id3 = id3
        self.id = player_id
        self.team = team
        if player_id != 1:
            self.id64 = 76561197960265728 + int(player_id)
        else:
            self.id64 = ""
        self.profile = Player.__STEAM_PROFILE_BASE_URL + str(self.id64)

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id3)
