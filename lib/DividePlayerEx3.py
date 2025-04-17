import numpy as np
from itertools import combinations
import random
from typing import List, Tuple, Dict


class Player:
    def __init__(self, id: int, name: str, cav_score: int, inf_score: int, arc_score: int):
        self.id = id
        self.name = name
        self.scores = {
            'cavalry': cav_score,
            'infantry': inf_score,
            'archer': arc_score
        }
        # 处理同分情况：优先骑兵>弓兵>步兵
        if cav_score == max(cav_score, inf_score, arc_score):
            self.primary = 'cavalry'
        elif arc_score == max(inf_score, arc_score):
            self.primary = 'archer'
        else:
            self.primary = 'infantry'
        self.primary_score = self.scores[self.primary]
        self.total_score = max(cav_score, inf_score, arc_score)

    def change_primary(self, new_primary: str):
        """修改玩家的主要职业"""
        self.primary = new_primary
        self.primary_score = self.scores[self.primary]


def load_players_from_data() -> List[Player]:
    """从给定数据创建玩家列表"""

    data = [
        ("[FRKZ] Roxy", 3700, 3000, 1000),
        ("[KR] Captain! My Captain.", 3700, 2800, 1000),
        ("[KR] 青衫客", 3500, 1000, 1000),
        ("章作之", 1000, 3000, 1000),
        ("交界地第一高手", 2200, 1000, 2000),
        ("[EA] C_urse", 3800, 1000, 1000),
        ("[FRKZ] Tupac", 4000, 1000, 1000),
        ("[HorN] 金璇", 1000, 1600, 1000),
        ("Faker", 3800, 1000, 1000),
        ("Xaxaxa", 3500, 1000, 1000),
        ("[FRKZ] chongfeng", 1000, 3000, 1000),
        ("[TO] 海德里希·冯·巴塞赫姆", 4000, 1000, 1000),
        ("大公鸡咪咪", 1000, 1800, 1000),
        ("[Xc] RS海豹", 3700, 1000, 1000),
        ("[KR] Legendarydogegg", 1000, 2200, 1000),
        ("[Vreg] Mein", 1000, 1000, 1000),
        ("出言吐词", 1000, 2000, 1000),
        ("[ARBT] Rocinante", 1000, 2500, 1000),
        ("尹志平", 3600, 3000, 1000),
        ("[TCHC] 圣城的幽灵蓝", 2500, 2000, 2500),
        ("[Han] 猩猩队长", 1000, 1000, 1000),
        ("黑色幽默", 1500, 1000, 1500),
        ("[TGoS] Acilec", 1000, 1000, 2800),
        ("ひむら　けんしん", 1000, 2300, 1000),
        ("[LSP] AFK", 3000, 1000, 1000),
        ("[DH] 月祭祀", 1000, 2400, 1000)
    ]

    # 随机选取12名玩家
    selected_data = random.sample(data, 12)
    return [Player(i, *player) for i, player in enumerate(selected_data)]


def balance_teams(players: List[Player]) -> Tuple[List[Player], List[Player], int]:
    """执行分组算法"""
    # 选择两个最高分玩家作为队长
    sorted_players = sorted(players, key=lambda x: -x.total_score)
    captain1, captain2 = sorted_players[:2]
    remaining = [p for p in players if p not in (captain1, captain2)]

    best_diff = float('inf')
    best_teams = None

    # 遍历所有可能组合
    for team_a_rest in combinations(remaining, 5):
        team_a = list(team_a_rest) + [captain1]
        team_b = [p for p in remaining if p not in team_a_rest] + [captain2]

        # 检查兵种平衡
        cav_diff = abs(
            sum(1 for p in team_a if p.primary == 'cavalry') -
            sum(1 for p in team_b if p.primary == 'cavalry')
        )
        arc_diff = abs(
            sum(1 for p in team_a if p.primary == 'archer') -
            sum(1 for p in team_b if p.primary == 'archer')
        )

        if cav_diff > 2 or arc_diff > 2:
            continue

        # 如果某队骑兵或弓兵超过2个，调整为次高分职业
        for team in [team_a, team_b]:
            cav_count = sum(1 for p in team if p.primary == 'cavalry')
            arc_count = sum(1 for p in team if p.primary == 'archer')

            # 调整多余的骑兵为步兵
            while cav_count > 2:
                for p in team:
                    if p.primary == 'cavalry':
                        p.change_primary('infantry')
                        cav_count -= 1
                        break

            # 调整多余的弓兵为步兵
            while arc_count > 2:
                for p in team:
                    if p.primary == 'archer':
                        p.change_primary('infantry')
                        arc_count -= 1
                        break

        # 计算评分差
        diff = abs(sum(p.primary_score for p in team_a) - sum(p.primary_score for p in team_b))
        if diff < best_diff:
            best_diff = diff
            best_teams = (team_a, team_b)
            if diff == 0:  # 找到完美解提前退出
                break

    return best_teams[0], best_teams[1], best_diff


def print_results(team_a: List[Player], team_b: List[Player], diff: int):
    """可视化输出分组结果"""
    print("\n=== 队伍A ===")
    captain_a = max(team_a, key=lambda x: x.total_score)
    print(f"★队长 ID:{captain_a.id} {captain_a.name} {captain_a.primary}({captain_a.total_score})")
    for p in sorted([p for p in team_a if p != captain_a], key=lambda x: -x.primary_score):
        print(
            f"ID:{p.id} {p.name.ljust(20)} {p.primary}({p.primary_score}) [C:{p.scores['cavalry']} I:{p.scores['infantry']} A:{p.scores['archer']}]")

    print("\n=== 队伍B ===")
    captain_b = max(team_b, key=lambda x: x.total_score)
    print(f"★队长 ID:{captain_b.id} {captain_b.name} {captain_b.primary}({captain_b.total_score})")
    for p in sorted([p for p in team_b if p != captain_b], key=lambda x: -x.primary_score):
        print(
            f"ID:{p.id} {p.name.ljust(20)} {p.primary}({p.primary_score}) [C:{p.scores['cavalry']} I:{p.scores['infantry']} A:{p.scores['archer']}]")

    # 统计职业分布
    stats = {
        'A': {'cav': 0, 'inf': 0, 'arc': 0},
        'B': {'cav': 0, 'inf': 0, 'arc': 0}
    }
    for p in team_a:
        stats['A'][p.primary[:3]] += 1
    for p in team_b:
        stats['B'][p.primary[:3]] += 1

    print(f"\n职业分布：骑兵(A:{stats['A']['cav']} B:{stats['B']['cav']}) "
          f"弓兵(A:{stats['A']['arc']} B:{stats['B']['arc']}) "
          f"步兵(A:{stats['A']['inf']} B:{stats['B']['inf']})")

    print(f"总分：A={sum(p.primary_score for p in team_a)} B={sum(p.primary_score for p in team_b)}")
    print(f"评分差：{diff}")


def main():
    print("=== 6v6比赛分组系统 ===")
    print("从数据集中随机选取12名玩家...")
    players = load_players_from_data()

    print("\n玩家初始数据：")
    for p in players:
        print(
            f"ID:{p.id} {p.name.ljust(20)} {p.primary}({p.total_score}) C:{p.scores['cavalry']} I:{p.scores['infantry']} A:{p.scores['archer']}")

    print("\n计算最优分组...")
    team_a, team_b, diff = balance_teams(players)
    print_results(team_a, team_b, diff)


if __name__ == "__main__":
    main()
