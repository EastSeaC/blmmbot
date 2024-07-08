import json

from aiohttp import web
from aiohttp.web_response import Response
from sqlalchemy import desc

from LogHelper import LogHelper
from init_db import get_session
from match_state import PlayerInfo, MatchState
from tables import DB_PlayerData

matchRouter = web.RouteTableDef()
sqlSession = get_session()

player_id_list = []


@matchRouter.post('/divide_players_to_2_group')
async def divide_players_to_2_group(req):
    data = await req.json()

    data = json.loads(data)

    scores_list = sqlSession.query(DB_PlayerData).filter(DB_PlayerData.playerId.in_(list(data))).order_by(
        desc(DB_PlayerData.rank)).all()
    list_a = []
    for i in scores_list:
        z: DB_PlayerData = i
        pm = PlayerInfo(z.__dict__)
        list_a.append(pm)
    MatchState.divide_player_ex(list_a)
    return Response(text='123')
    pass


@matchRouter.post('/upload_player_list')
async def upload_player_list(req):
    data = await req.json()

    data = json.loads(data)
    global player_id_list
    player_id_list = list(data)

    LogHelper.log('玩家player ids 上传收到 ')
    return Response(text='123')
    pass
