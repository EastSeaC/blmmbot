class SelectPlayerMatchData:
    is_running = False

    first_team_master = ''
    second_team_master = ''

    first_team_player_ids = []
    second_team_player_ids = []

    origin_list = []
    total_list = []
    need_to_select = []

    cur_select_master = 0
    cur_index = 0
    select_order = '2112212121'

    cur_waiting = 0
    # max_waiting = 12
    max_waiting = 15

    data = []

    @classmethod
    def get_cur_select_master(cls):
        try:
            print('选人索引', cls.cur_index)
            if cls.cur_index <= len(cls.select_order):
                x = cls.select_order[cls.cur_index]
            else:
                x = -1
            print('选人索引x', x)
            return x
        except Exception as e:
            print(repr(e))
            return -1

    @classmethod
    def get_cur_select_master_ex(cls):
        try:
            print('选人索引', cls.cur_index)
            if cls.cur_index <= len(cls.select_order):
                x = cls.select_order[cls.cur_index]
                return cls.second_team_master if x == '2' else cls.first_team_master
            else:
                x = -1
            print('选人索引x', x)
            return x
        except Exception as e:
            print(repr(e))
            return -1

    @classmethod
    def start_run(cls):
        cls.is_running = True

    @classmethod
    def close_run(cls):
        cls.is_running = False

    def __init__(self):
        self.first_team_master = ''
        self.first_team_player_ids = []
        self.first_team_culture = ''

        self.second_team_master = ''
        self.second_team_player_ids = []
        self.second_team_culture = ''

        self.origin_list = []  # 原list不要改动
        self.total_list = []
        self.need_to_select = []  # 不断减少

        self.select_order = '2112212121'
        self.cur_index = 0

    @classmethod
    def get_cur_index(cls):
        return cls.cur_index

    @classmethod
    def add_attacker(cls, player_id: str):
        cls.cur_waiting = 0
        cls.cur_index += 1

        cls.first_team_player_ids.append(player_id)
        cls.total_list.append(player_id)
        cls.need_to_select = list(set(cls.origin_list) - set(cls.total_list))

    @classmethod
    def add_defender(cls, player_id: str):
        cls.cur_waiting = 0
        cls.cur_index += 1

        cls.second_team_player_ids.append(player_id)
        cls.total_list.append(player_id)
        cls.need_to_select = list(set(cls.origin_list) - set(cls.total_list))
