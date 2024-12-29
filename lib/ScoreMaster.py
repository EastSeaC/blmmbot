from sqlalchemy import select

from convert.PlayerMatchData import TPlayerMatchData
from init_db import get_session
from lib.LogHelper import LogHelper
from tables import DB_Matchs
from tables.ScoreLimit import DB_ScoreLimit


async def calculate_score(match_data: DB_Matchs, player_data: TPlayerMatchData):
    if player_data is None or match_data is None:
        LogHelper.log("【calculate_score】空引用")
        return 0

    with get_session() as sql_session:
        result = sql_session.execute(select(DB_ScoreLimit).where(DB_ScoreLimit.score_type == 'default')).first()

        score_limit: DB_ScoreLimit = result[0]


    pass
