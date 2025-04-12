import numpy as np
from itertools import combinations
import random


class Divide_Player_Item:
    def __init__(self, id, cav_score, inf_score, arc_score):
        self.id = id
        self.scores = {
            'cavalry': cav_score,
            'infantry': inf_score,
            'archer': arc_score
        }
        self.primary = max(self.scores, key=self.scores.get)
        self.primary_score = self.scores[self.primary]


class Divide_Style_American:
    first_team_player: list[Divide_Player_Item]
    second_team_player: list[Divide_Player_Item]
    score_diff = 0

    @classmethod
    def DividePlayers(cls, list_a: list):
        a, b, c = balance_teams(list_a)
        cls.first_team_player = a
        cls.second_team_player = b
        cls.score_diff = c


def generate_random_players(num_players=12):
    """生成符合比赛要求的随机玩家数据"""
    players = []
    for i in range(num_players):
        # 确保每个职业至少有2名玩家（避免极端分布）
        if i < 2:
            cav = random.randint(2000, 3000)
            inf = random.randint(0, min(1800, cav - 1))
            arc = random.randint(0, min(1800, cav - 1))
        elif i < 4:
            inf = random.randint(2000, 3000)
            cav = random.randint(0, min(1800, inf - 1))
            arc = random.randint(0, min(1800, inf - 1))
        elif i < 6:
            arc = random.randint(2000, 3000)
            cav = random.randint(0, min(1800, arc - 1))
            inf = random.randint(0, min(1800, arc - 1))
        else:
            # 随机生成但避免评分完全相同
            cav = random.randint(0, 3000)
            inf = random.randint(0, 3000)
            arc = random.randint(0, 3000)
            while len(set([cav, inf, arc])) < 2:  # 确保至少有两个不同分数
                arc = random.randint(0, 3000)

        players.append((cav, inf, arc))
    return players


def balance_teams(players):
    """核心分组算法"""
    players = [Divide_Player_Item(i, *scores) for i, scores in enumerate(players)]

    # 先计算所有可能的组合（优化：提前过滤明显不平衡的组合）
    all_players = set(players)
    best_diff = float('inf')
    best_teams = (None, None)

    # 优化：按骑兵/弓兵数量预筛选
    cav_count = sum(1 for p in players if p.primary == 'cavalry')
    arc_count = sum(1 for p in players if p.primary == 'archer')

    # 生成候选组合时优先考虑可能满足职业平衡的
    for team_a in combinations(players, 6):
        team_a = list(team_a)
        team_b = [p for p in players if p not in team_a]

        # 快速检查职业平衡
        a_cav = sum(1 for p in team_a if p.primary == 'cavalry')
        a_arc = sum(1 for p in team_a if p.primary == 'archer')
        b_cav = cav_count - a_cav
        b_arc = arc_count - a_arc

        if abs(a_cav - b_cav) > 1 or abs(a_arc - b_arc) > 1:
            continue

        # 计算评分差
        diff = abs(sum(p.primary_score for p in team_a) - sum(p.primary_score for p in team_b))
        if diff < best_diff:
            best_diff = diff
            best_teams = (team_a, team_b)
            if diff == 0:  # 找到完美解提前退出
                break

    return best_teams[0], best_teams[1], best_diff


def print_team_info(team_a, team_b, diff):
    """打印分组信息"""
    print("\n队伍A（评分总和：{:.0f}）：".format(sum(p.primary_score for p in team_a)))
    for p in sorted(team_a, key=lambda x: -x.primary_score):
        print(
            f"ID:{p.id} {p.primary}({p.primary_score}) [C:{p.scores['cavalry']} I:{p.scores['infantry']} A:{p.scores['archer']}]")

    print("\n队伍B（评分总和：{:.0f}）：".format(sum(p.primary_score for p in team_b)))
    for p in sorted(team_b, key=lambda x: -x.primary_score):
        print(
            f"ID:{p.id} {p.primary}({p.primary_score}) [C:{p.scores['cavalry']} I:{p.scores['infantry']} A:{p.scores['archer']}]")

    print(
        f"\n职业分布：骑兵(A:{sum(1 for p in team_a if p.primary == 'cavalry')} vs B:{sum(1 for p in team_b if p.primary == 'cavalry')}) "
        f"弓兵(A:{sum(1 for p in team_a if p.primary == 'archer')} vs B:{sum(1 for p in team_b if p.primary == 'archer')})")
    print(f"评分差：{diff}")


# 测试用例
def test_case():
    # 生成随机数据
    player_scores = generate_random_players()
    print("生成的玩家数据：")
    for i, (c, i, a) in enumerate(player_scores):
        primary = ['cavalry', 'infantry', 'archer'][np.argmax([c, i, a])]
        print(f"玩家{i}: {primary} (C:{c} I:{i} A:{a})")

    # 运行分组算法
    team_a, team_b, diff = balance_teams(player_scores)

    # 打印结果
    print_team_info(team_a, team_b, diff)


# 运行测试
if __name__ == "__main__":
    test_case()
