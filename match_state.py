from datetime import datetime
from enum import Enum
from random import randint

from LogHelper import LogHelper


class MatchConditionEx:
    server_name = None
    end_game: bool = False
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

        self.waiting_list = {}

        self.confirmed: bool = False  # 游戏已初始化，人数到齐.
        self.match_over: bool = False  # 比赛结束？
        self.documented: bool = False  # 归档完成?

        self.first_player_join_time: datetime
        pass

    # 添加玩家到等候列表
    def add_player_to_wait_list(self, user_id):
        self.waiting_list[user_id] = datetime.now()
        self.check_state()

    def remove_player_from_wait_list(self, user_id):
        if user_id in self.waiting_list:
            self.waiting_list.pop(user_id)

    def get_cur_player_num_in_wait_list(self):
        return len(self.waiting_list)

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
        if len(self.waiting_list) == self.need_num:
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
            if self.documented:
                self.state = MatchCondition.WaitingJoin
                self.reset_match()

        return self.state

    def divie_player(self):
        list_player = []
        for i in self.waiting_list.keys():
            list_player.append(PlayerBasicInfo(
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
            k: PlayerBasicInfo = i
            print(k.score, k.user_id)
        print('a*' * 20)
        x, y = min_diff_partition(a)
        m = []
        for i in x:
            k: PlayerBasicInfo = i
            m.append(k.user_id)
            print(k.score, k.user_id)

        print('*' * 20)
        n = []
        for i in y:
            k: PlayerBasicInfo = i
            n.append(k.user_id)
            print(k.score, k.user_id)
        return m, n

    @staticmethod
    def divide_player_ex(a: list):
        """
        用于分组, 第一组是 攻击者的 user_id， 第二组是 防御者的 userid
        """
        div = DivideData()
        print('[divide_player_ex|out]-shift')
        for i in a:
            # print(i.score, i.user_id, i.user_name)
            k: PlayerBasicInfo = i
            # print(k.score, k.user_id, k.user_name)
        print('a*' * 20)
        x, y = min_diff_partition(a)

        attacker_names = []
        attacker_score_temp = 0
        defender_names = []
        defender_score_temp = 0
        m = []
        for i in x:
            k: PlayerBasicInfo = i
            m.append(k.user_id)
            attacker_score_temp += k.score
            attacker_names.append(k.user_name)

            print(k.score, k.user_id)

            div.add_attacker_info(k.user_name, k.score, k.player_id)  # 添加 积分块

        print('*' * 20)
        n = []
        for i in y:
            k: PlayerBasicInfo = i
            n.append(k.user_id)
            defender_score_temp += k.score
            defender_names.append(k.user_name)
            print(k.score, k.user_id)

            div.add_defender_info(k.user_name, k.score, k.player_id)  # 添加 积分块

        div.attacker_list = m
        div.attacker_names = attacker_names
        div.defender_list = n
        div.attacker_scores = attacker_score_temp
        div.defend_scores = defender_score_temp
        div.defender_names = defender_names
        return div

    @property
    def get_match_num(self):
        return len(self.waiting_list)

    @property
    def is_start_match(self):
        return self.state == 1


class PlayerBasicInfo:
    def __init__(self, player_dict: dict) -> None:
        self.score = player_dict.get('score', 0)
        self.user_id = player_dict.get('user_id', '62a')  # kook的用户id
        self.user_name = player_dict.get('username', 'baga')
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


class DivideData:
    def __init__(self):
        self.attacker_list = []
        self.defender_list = []
        self.attacker_scores: int = 0
        self.defend_scores: int = 0
        self.attacker_names = []
        self.defender_names = []

        self.attacker_info_block = []
        self.defender_info_block = []

    def __str__(self):
        return f"attacker_names:{self.attacker_names} defender_names:{self.defender_names}, list:{self.attacker_list},{self.defender_list}, attacker_scores:{self.attacker_scores}, defend_scores:{self.defend_scores}, diff {self.attacker_scores - self.defend_scores}"

    def add_attacker_info(self, attacker_name: str, score: int, player_id: str):
        self.attacker_info_block.append([attacker_name, score, player_id])

    def add_defender_info(self, defender_name: str, score: int, player_id: str):
        self.defender_info_block.append([defender_name, score, player_id])

    def get_first_team_player_ids(self):
        return [defender_info[2] for defender_info in self.attacker_info_block]

    def get_second_team_player_ids(self):
        return [defender_info[2] for defender_info in self.defender_info_block]

    def get_attacker_names(self):
        return '玩家名称\n' + '\n'.join([defender_info[0] for defender_info in self.attacker_info_block])

    def get_attacker_scores(self):
        return '当前分数\n' + '\n'.join([str(defender_info[1]) for defender_info in self.attacker_info_block])

    def get_defender_names(self):
        return '玩家名称\n' + '\n'.join([defender_info[0] for defender_info in self.defender_info_block])

    def get_defender_scores(self):
        return '当前分数\n' + '\n'.join([str(defender_info[1]) for defender_info in self.defender_info_block])


def sorted_aux(player):
    return player.score


def min_diff_partition(nums):
    if isinstance(nums[0], PlayerBasicInfo):
        num_list = sorted(nums[:], key=sorted_aux)
        LogHelper.log('排序使用key')
    else:
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
