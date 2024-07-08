from datetime import datetime
from enum import Enum
from random import randint


class MatchConditionEx:
    server_name = None
    state: bool = False
    data = None
    data2 = None
    round_count = 0


class MatchCondition(Enum):
    NoPlayer = 0
    WaitingJoin = 1
    DividePlayer = 2  # 分派人员
    ConfirmMatch = 3  # 让服务器刷新数据，传递人员列表给服务器
    Started = 4  # 已启动
    Documenting = 5  # 归档数据


class MatchState:
    def __init__(self) -> None:
        self.state: MatchCondition = MatchCondition.WaitingJoin
        self.player_number: int = 0
        self.attack_num: int = 0
        self.attack_list = []
        self.real_attack_list = []  # 真实情况
        self.defend_num: int = 0
        self.defend_list = []
        self.need_num: int = 12  # 所需玩家数

        self.waitting_list = {}

        self.confirmed: bool = False  # 游戏已初始化，人数到齐.
        self.match_over: bool = False  # 比赛结束？
        self.documentd: bool = False  # 归档完成?

        self.first_player_join_time: datetime
        pass

    # 添加玩家到等候列表
    def add_player_to_wait_list(self, user_id):
        self.waitting_list[user_id] = True
        self.check_state()

    def remove_player_from_wait_list(self, user_id):
        if user_id in self.waitting_list:
            self.waitting_list.pop()

    def get_cur_player_num_in_wait_list(self):
        return len(self.waitting_list)

    def add_player_num(self):
        self.player_number += 1

    def minus_player_num(self):
        self.player_number -= 1

    # A队人数管理
    def add_a_team_player_num(self):
        self.attack_num += 1

    def add_a_team_player(self, kook_id: str):
        self.attack_list.append(kook_id)
        self.attack_num = self.attack_list.count()

    def set_player_num(self, num: int):
        self.player_number = num

    def reset_match(self):
        self.__init__()

    def check_state(self):
        if len(self.waitting_list) == self.need_num:
            self.state = MatchCondition.DividePlayer
        elif self.state == MatchCondition.DividePlayer:
            self.divie_player()
            self.state = MatchCondition.ConfirmMatch
        elif self.state is MatchCondition.ConfirmMatch:
            if self.confirmed:
                self.state = MatchCondition.Started
        elif self.state is MatchCondition.Started:
            if self.match_over:
                self.state = MatchCondition.Documenting
        elif self.state is MatchCondition.Documenting:
            if self.documentd:
                self.state = MatchCondition.WaitingJoin
                self.reset_match()

        return self.state

    def divie_player(self):
        list_player = []
        for i in self.waitting_list.keys():
            list_player.append(PlayerInfo(
                {'score': randint(10, 20), 'user_id': i}))
        a, b = min_diff_partition(list_player)
        self.attack_list = a
        self.defend_list = b
        # print(a, b)
        for i in a:
            print(i.score, i.user_id)
        print('*' * 20)
        for i in b:
            print(i.score, i.user_id)
        pass

    @staticmethod
    def divide_player_test(self, a: list):
        for i in a:
            k: PlayerInfo = i
            print(k.score, k.user_id)
        print('a*' * 20)
        x, y = min_diff_partition(a)
        m = []
        for i in x:
            k: PlayerInfo = i
            m.append(k.user_id)
            print(k.score, k.user_id)

        print('*' * 20)
        n = []
        for i in y:
            k: PlayerInfo = i
            n.append(k.user_id)
            print(k.score, k.user_id)
        return m, n

    @staticmethod
    def divide_player_ex(a: list):
        """
        用于分组
        """
        for i in a:
            k: PlayerInfo = i
            print(k.score, k.user_id)
        print('a*' * 20)
        x, y = min_diff_partition(a)
        m = []
        for i in x:
            k: PlayerInfo = i
            m.append(k.user_id)
            print(k.score, k.user_id)

        print('*' * 20)
        n = []
        for i in y:
            k: PlayerInfo = i
            n.append(k.user_id)
            print(k.score, k.user_id)
        return m, n

    @property
    def is_start_match(self):
        return self.state == 1


class PlayerInfo:
    def __init__(self, player_dict: dict) -> None:
        self.score = player_dict.get('score', 0)
        self.user_id = player_dict.get('user_id', '62a')  # kook的用户id
        self.player_id = player_dict.get('playerId')  # 游戏Id
        self.kill = player_dict.get('kill', 0)
        self.death = player_dict.get('death', 0)
        self.assist = player_dict.get('assist', 0)  # 辅助
        pass

    def __lt__(self, other):
        return self.score < other.score

    @staticmethod
    def convert(self, z):
        pass


def min_diff_partition(nums):
    num_list = sorted(nums[:])
    first_list = []
    second_list = []
    first_list.append(num_list.pop(-1))
    second_list.append(num_list.pop(-1))
    while len(num_list):
        second_list.append(num_list.pop(-1))
        first_list.append(num_list.pop(-1))
    return first_list, second_list


if __name__ == '__main__':
    # a, b = min_diff_partition([100, 20, 78, 60, 32, 54, 69, 78])
    # a, b = min_diff_partition([0]*12)
    # print(a, b, sum(a), sum(b))

    dt = datetime.fromtimestamp(1708247557000 / 1000.0)

    # 打印日期和时间
    print(dt)

    # list_player = []
    # for i in range(12):
    #     list_player.append(PlayerInfo(
    #         {'score': randint(10, 20), 'user_id': str(i)}))
    # A, B = min_diff_partition(list_player)
    # for i in A:
    #     k: PlayerInfo = i
    #     print(k.score, k.user_id)

    # print('*'*20)
    # for i in B:
    #     k: PlayerInfo = i
    #     print(k.score, k.user_id)
