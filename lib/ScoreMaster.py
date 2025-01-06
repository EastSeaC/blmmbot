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
    # print(f"value : {value} {score_name}")
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

        kill_score = clamp(score_limit.max_kill_score * player_data.kill / enemy_total_spawn_times,
                           score_limit.min_kill_score,
                           score_limit.max_kill_score)

        death_score = clamp(
            score_limit.max_death_score * ((player_data.spawn_times - player_data.death) // player_data.spawn_times),
            score_limit.min_death_score,
            score_limit.max_death_score)

        assist_score = clamp(
            score_limit.max_assist_score * player_data.assist / ally_total_assist_times,
            score_limit.min_assist_score,
            score_limit.max_assist_score,
        )

        damage_score = clamp(
            score_limit.max_damage_score * (
                    player_data.damage / (score_limit.per_round_damage * player_data.total_rounds)),
            score_limit.min_damage_score,
            score_limit.max_damage_score,
            'damage'
        )

        sum_score = ceil(kill_score + death_score + assist_score + damage_score)
        score_dick = {
            'player_name': player_data.player_name,
            'kill_score': kill_score,
            'death_score': death_score,
            'assist_score': assist_score,
            'damage_score': damage_score,
        }
        print(json.dumps(score_dick, indent=4, ensure_ascii=False))
        return sum_score
    pass
