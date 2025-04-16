class SelectPlayerMatchData:
    def __init__(self):
        self.first_team_player_ids = []
        self.first_team_culture = ''

        self.second_team_player_ids = []
        self.second_team_culture = ''

        self.origin_list = []  # 原list不要改动
        self.total_list = []
        self.need_to_select = []  # 不断减少

        self.select_order = '2112212121'
        self.cur_index = 0

    def add_attacker(self, player_id: str):
        self.first_team_player_ids.append(player_id)
        self.total_list.append(player_id)
        self.need_to_select = list(set(self.origin_list) - set(self.total_list))

    def add_defender(self, player_id: str):
        self.second_team_player_ids.append(player_id)
        self.total_list.append(player_id)
        self.need_to_select = list(set(self.origin_list) - set(self.total_list))
