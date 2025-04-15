import json
from math import ceil

from sqlalchemy import select

from convert.PlayerMatchData import TPlayerMatchData
from init_db import get_session
from lib.BannerlordTeam import BannerlordTeam
from lib.LogHelper import LogHelper
from tables.MatchInfo import MatchSumData
from tables.ScoreLimit import DB_ScoreLimit


def clamp(value, lower_bound, upper_bound, score_name: str = ''):
    if score_name != '':
        print(f"value : {value} {score_name}")
    return max(lower_bound, min(value, upper_bound))


def calculate_score(all_player_data: MatchSumData, player_data: TPlayerMatchData):
    """
    X计算玩家比赛分数
    """
    if player_data is None or all_player_data is None:
        LogHelper.log("【calculate_score】空引用")
        return 0

    with get_session() as sql_session:
        result = sql_session.execute(select(DB_ScoreLimit).where(DB_ScoreLimit.score_type == 'default')).first()

        score_limit: DB_ScoreLimit = result[0]

        enemy_total_spawn_times = all_player_data.second_team_total_spawn_times if player_data.team == BannerlordTeam.FirstTeam else all_player_data.first_team_total_spawn_times
        ally_total_assist_times = all_player_data.first_team_total_assist_times if player_data.team == BannerlordTeam.FirstTeam else all_player_data.second_team_total_spawn_times

        # 计算队伍分数
        team_score = (all_player_data.attacker_rounds - all_player_data.defender_rounds) * 30
        if player_data.team == BannerlordTeam.FirstTeam:
            if all_player_data.attacker_rounds <= all_player_data.defender_rounds:
                team_score = -team_score
        elif player_data.team == BannerlordTeam.SecondTeam:
            if all_player_data.attacker_rounds >= all_player_data.defender_rounds:
                team_score = -team_score

        kill_score = clamp(score_limit.max_kill_score * player_data.kill / enemy_total_spawn_times,
                           score_limit.min_kill_score,
                           score_limit.max_kill_score)

        death_score = clamp(
            score_limit.max_death_score * ((player_data.spawn_times - player_data.death + 1) / player_data.spawn_times),
            score_limit.min_death_score,
            score_limit.max_death_score,
            # 'death_score'
        )

        if ally_total_assist_times == 0:
            assist_score = 0
        else:
            assist_score = clamp(
                score_limit.max_assist_score * player_data.assist / ally_total_assist_times,
                score_limit.min_assist_score,
                score_limit.max_assist_score,
            )

        damage_score = clamp(
            score_limit.max_damage_score * (
                    player_data.damage / (score_limit.per_round_damage * all_player_data.total_round)),
            score_limit.min_damage_score,
            score_limit.max_damage_score,
            # 'damage'
        )

        match_lose_minus = score_limit.failed_minus if player_data.is_lose else 0
        sum_score = ceil(kill_score + death_score + assist_score + damage_score) + team_score - match_lose_minus
        score_dick = {
            'player_id': player_data.player_id,
            'player_name': player_data.player_name,
            'kill_score': kill_score,
            'death_score': death_score,
            'assist_score': assist_score,
            'damage_score': damage_score,
            'match_lose_minus': match_lose_minus,
            'team_score': team_score,
            'sum_score': sum_score,
        }
        print(json.dumps(score_dick, indent=4, ensure_ascii=False))
        return sum_score
    pass
