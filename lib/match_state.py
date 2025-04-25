import random
from datetime import datetime
from enum import Enum
from random import randint

from lib.LogHelper import LogHelper


class MatchConditionEx:
    server_name = None
    end_game: bool = False
    data = None
    data2 = None
    round_count = 0

    attacker_score = 0
    defender_score = 0

    blmm_1 = None
    blmm_2 = None
    blmm_3 = None


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
    def divide_player_test(a: list):
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
        # print('*' * 20)
        x, y = min_diff_partition(a)

        # 随机交换一名队员
        if len(a) >= 10:
            exchange_index = randint(2, 5)
            exchange_item = x[exchange_index]
            x[exchange_index] = y[exchange_index]
            y[exchange_index] = exchange_item

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
            div.add_first_team(k)
            div.add_attacker_info(k.user_name, k.score, k.player_id, k.user_id)  # 添加 积分块

        print('*' * 20)
        n = []
        for i in y:
            k: PlayerBasicInfo = i
            n.append(k.user_id)
            defender_score_temp += k.score
            defender_names.append(k.user_name)
            print(k.score, k.user_id)

            div.add_second_team(k)
            div.add_defender_info(k.user_name, k.score, k.player_id, k.user_id)  # 添加 积分块

        # while div.not_balance():
        #     div.balance()

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

        self.first_troop = player_dict.get('first_troop', 0)
        self.second_troop = player_dict.get('second_troop', 0)
        pass

    def __lt__(self, other):
        return self.score < other.score

    @property
    def is_knight_only(self):
        return (self.first_troop == 2 and self.second_troop < 2) or (
                self.first_troop < 2 and self.second_troop == 2)

    @property
    def is_archer_only(self):
        return (self.first_troop == 3 and self.second_troop < 2) or (
                self.first_troop < 2 and self.second_troop == 3)

    @property
    def is_both_knight_and_archer(self):
        return self.first_troop + self.second_troop == 5

    @property
    def is_infantry(self):
        return self.first_troop < 2 and self.second_troop < 2

    @property
    def is_contain_knight(self):
        return self.first_troop == 2 or self.second_troop == 2

    @property
    def is_contain_archer(self):
        return self.first_troop == 3 or self.second_troop == 3

    @property
    def knight_count(self):
        return 1 if self.is_contain_knight else 0

    @property
    def archer_count(self):
        return 1 if self.is_contain_archer else 0

    @staticmethod
    def convert(self, z):
        pass

    def count_knight_archer(self):
        # 返回一个元组，分别是骑兵数量和射手数量
        knight_count = 0
        archer_count = 0

        if self.first_troop == 2 or self.second_troop == 2:
            knight_count += 1
        if self.first_troop == 3 or self.second_troop == 3:
            archer_count += 1

        return knight_count, archer_count


# 分割列表的函数
def split_players(players: list):
    # 按照骑兵和射手类型分类
    knights = []
    archers = []
    others = []

    # 统计玩家的骑兵、射手数量，并按类型分组
    for player in players:
        knight_count, archer_count = player.count_knight_archer()
        if knight_count > 0:
            knights.append(player)
        if archer_count > 0:
            archers.append(player)
        if knight_count == 0 and archer_count == 0:
            others.append(player)

    # 确保分配时，骑兵和射手的数量平衡
    team1 = []
    team2 = []
    score_team1 = 0
    score_team2 = 0
    knight_team1 = 0
    knight_team2 = 0
    archer_team1 = 0
    archer_team2 = 0

    # 贪心分配骑兵
    for player in knights:
        if knight_team1 <= knight_team2:
            team1.append(player)
            knight_team1 += 1
            score_team1 += player.score
        else:
            team2.append(player)
            knight_team2 += 1
            score_team2 += player.score

    # 贪心分配射手
    for player in archers:
        if archer_team1 <= archer_team2:
            team1.append(player)
            archer_team1 += 1
            score_team1 += player.score
        else:
            team2.append(player)
            archer_team2 += 1
            score_team2 += player.score

    # 分配其他玩家
    for player in others:
        if len(team1) < 6:
            team1.append(player)
            score_team1 += player.score
        elif len(team2) < 6:
            team2.append(player)
            score_team2 += player.score

    # 如果两队人数不等，尝试平衡分数
    while len(team1) < 6 or len(team2) < 6:
        # 剩余的没有分配的玩家
        remaining_players = [p for p in players if p not in team1 and p not in team2]

        # 确保剩余玩家没有重复
        remaining_players_set = set(remaining_players)

        # 排序剩余玩家，优先考虑平衡两队的分数差
        remaining_players_sorted = sorted(remaining_players_set, key=lambda p: abs(score_team1 - score_team2),
                                          reverse=True)

        for player in remaining_players_sorted:
            if len(team1) < 6:
                team1.append(player)
                score_team1 += player.score
            elif len(team2) < 6:
                team2.append(player)
                score_team2 += player.score

    return team1, team2, score_team1, score_team2


def contain_both_type(a: list):
    return any(p.is_both_knight_and_archer for p in a)


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
        self.first_team = []
        self.second_team = []

    def __str__(self):
        return f"attacker_names:{self.attacker_names} defender_names:{self.defender_names}, list:{self.attacker_list},{self.defender_list}, attacker_scores:{self.attacker_scores}, defend_scores:{self.defend_scores}, diff {self.attacker_scores - self.defend_scores}"

    def add_first_team(self, s: PlayerBasicInfo):
        self.first_team.append(s)

    def add_second_team(self, s: PlayerBasicInfo):
        self.second_team.append(s)

    def add_attacker_info(self, attacker_name: str, score: int, player_id: str, kook_id: str = '-1'):
        self.attacker_info_block.append([attacker_name, score, player_id, kook_id])

    def add_defender_info(self, defender_name: str, score: int, player_id: str, kook_id: str = '-1'):
        self.defender_info_block.append([defender_name, score, player_id, kook_id])

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

    def not_balance(self):
        first_sum_knight = sum(p.knight_count for p in self.first_team)
        second_sum_knight = sum(p.knight_count for p in self.second_team)

        first_sum_archer = sum(p.archer_count for p in self.first_team)
        second_sum_archer = sum(p.archer_count for p in self.second_team)

        if abs(first_sum_archer - second_sum_archer) > 1 or abs(first_sum_knight - second_sum_knight) > 1:
            return True
        return False
        pass

    def exchange_player(self, a: list):
        for index, p in a:
            temp_one = self.first_team[index]
            self.first_team[index] = self.second_team[index]
            self.second_team[index] = temp_one

            LogHelper.log('*' * 10 + f'exchange {index}' + '*' * 10)

    def balance(self):
        first_sum_knight = sum(p.knight_count for p in self.first_team)
        second_sum_knight = sum(p.knight_count for p in self.second_team)

        first_sum_archer = sum(p.archer_count for p in self.first_team)
        second_sum_archer = sum(p.archer_count for p in self.second_team)

        if abs(first_sum_archer - second_sum_archer) > 1 and abs(first_sum_knight - second_sum_knight) > 1:
            if first_sum_archer > second_sum_archer:
                matching_elements = [(index, p) for index, p in enumerate(self.first_team) if
                                     p.is_both_knight_and_archer]
                count_of_matching_elements = len(matching_elements)
                if count_of_matching_elements == 0:  # 说明没有 骑兵|射手， 选择单一兵种
                    matching_elements = [(index, p) for index, p in enumerate(self.first_team) if
                                         p.is_contain_archer]
                    count_of_matching_elements = len(matching_elements)
                    picked_matching_elements = random.sample(matching_elements, k=count_of_matching_elements // 2)
                    self.exchange_player(picked_matching_elements)
                    # 交换部分骑兵
                    matching_elements = [(index, p) for index, p in enumerate(self.first_team) if
                                         p.is_contain_knight]
                    count_of_matching_elements = len(matching_elements)
                    picked_matching_elements = random.sample(matching_elements, k=count_of_matching_elements // 2)
                    pass
                else:
                    # 采样出不重复的 一小半
                    picked_matching_elements = random.sample(matching_elements, k=count_of_matching_elements // 2)
                    self.exchange_player(picked_matching_elements)
            else:
                matching_elements = [(index, p) for index, p in enumerate(self.second_team) if
                                     p.is_both_knight_and_archer]

        pass


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
