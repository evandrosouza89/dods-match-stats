class Match:
    def __init__(self, start_time_stamp, end_time_stamp, map_name):
        # Basic match information
        self.start_time_stamp = start_time_stamp
        self.end_time_stamp = end_time_stamp
        self.map_name = map_name
        self.team_allies_team_score = 0
        self.team_axis_team_score = 0
        self.team_allies_tick_score = None
        self.team_axis_tick_score = None
        self.team_allies_players = set()
        self.team_axis_players = set()
        self.spectators = set()

        # Events
        self.attack_event_list = []
        self.kill_event_list = []
        self.domination_event_list = []
        self.revenge_event_list = []
        self.connection_event_list = []
        self.disconnection_event_list = []
        self.entered_the_game_event_list = []
        self.steam_user_id_validated_event_list = []
        self.suicide_event_list = []
        self.joined_team_event_list = []
        self.changed_role_event_list = []
        self.changed_name_event_list = []
        self.say_event_list = []
        self.say_team_event_list = []
        self.cap_block_event_list = []
        self.captured_loc_event_list = []
        self.round_win_event_list = []
        self.tick_score_event_list = []

        # Stats
        self.adr_stat_list = []
        self.kill_stat_list = []
        self.team_score_stat_list = []
        self.weapon_stat_list = []
        self.streak_stat_list = []
