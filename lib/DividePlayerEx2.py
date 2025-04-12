import numpy as np
from itertools import combinations
import random
from typing import List, Tuple


class Divide_Player_Item2:
    def __init__(self, id: str, cav_score: int, inf_score: int, arc_score: int):
        self.id = id
        self.scores = {
            'cavalry': cav_score,
            'infantry': inf_score,
            'archer': arc_score
        }
        self.primary = max(self.scores, key=self.scores.get)
        self.primary_score = self.scores[self.primary]
        self.total_score = max(cav_score, inf_score, arc_score)


def generate_players(num_players: int = 12) -> List[Tuple[int, int, int]]:
    """生成包含两个高分队长的随机玩家数据"""
    players = []
    # 生成两个明显高分的队长
    for _ in range(2):
        main_score = random.randint(2800, 3000)
        other_scores = [random.randint(0, main_score - 200) for _ in range(2)]
        scores = random.sample([main_score] + other_scores, 3)
        players.append(tuple(scores))

    # 生成其余玩家
    for _ in range(num_players - 2):
        while True:
            scores = [random.randint(0, 3000) for _ in range(3)]
            if len(set(scores)) >= 2:
                players.append(tuple(scores))
                break
    return players


def balance_teams(players_data: List[Tuple[str, int, int, int]]) -> Tuple[
    List[Divide_Player_Item2], List[Divide_Player_Item2], int]:
    """执行分组算法"""
    # players = [Divide_Player_Item2(i, *scores) for i, scores in enumerate(players_data)]
    players = [Divide_Player_Item2(kid, score_a, score_b, score_c) for kid, score_a, score_b, score_c in players_data]
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

        if cav_diff > 1 or arc_diff > 1:
            continue

        # 计算评分差
        diff = abs(sum(p.primary_score for p in team_a) - sum(p.primary_score for p in team_b))
        if diff < best_diff:
            best_diff = diff
            best_teams = (team_a, team_b)
            if diff == 0:
                break

    return best_teams[0], best_teams[1], best_diff


def print_results(team_a: List[Divide_Player_Item2], team_b: List[Divide_Player_Item2], diff: int):
    """可视化输出分组结果"""
    print("\n=== 队伍A ===")
    captain_a = max(team_a, key=lambda x: x.total_score)
    print(f"★队长 ID:{captain_a.id} {captain_a.primary}({captain_a.total_score})")
    for p in sorted([p for p in team_a if p != captain_a], key=lambda x: -x.primary_score):
        print(
            f"ID:{p.id} {p.primary}({p.primary_score}) [C:{p.scores['cavalry']} I:{p.scores['infantry']} A:{p.scores['archer']}]")

    print("\n=== 队伍B ===")
    captain_b = max(team_b, key=lambda x: x.total_score)
    print(f"★队长 ID:{captain_b.id} {captain_b.primary}({captain_b.total_score})")
    for p in sorted([p for p in team_b if p != captain_b], key=lambda x: -x.primary_score):
        print(
            f"ID:{p.id} {p.primary}({p.primary_score}) [C:{p.scores['cavalry']} I:{p.scores['infantry']} A:{p.scores['archer']}]")

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
          f"弓兵(A:{stats['A']['arc']} B:{stats['B']['arc']})")
    print(f"总分：A={sum(p.primary_score for p in team_a)} B={sum(p.primary_score for p in team_b)}")
    print(f"评分差：{diff}")


def main():
    print("=== 6v6比赛分组系统 ===")
    print("生成随机玩家数据...")
    players_data = generate_players()

    print("\n玩家初始数据：")
    for i, (c, i, a) in enumerate(players_data):
        primary = ['cavalry', 'infantry', 'archer'][np.argmax([c, i, a])]
        print(f"ID:{i} {primary}({max(c, i, a)}) C:{c} I:{i} A:{a}")

    print("\n计算最优分组...")
    team_a, team_b, diff = balance_teams(players_data)
    print_results(team_a, team_b, diff)


if __name__ == "__main__":
    main()
