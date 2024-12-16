import datetime
import json

from aiohttp import web
from aiohttp.web_response import Response
from sqlalchemy import desc, func

from LogHelper import LogHelper
from entity.webEntity.ControllerResponse import ControllerResponse
from init_db import get_session
from match_state import PlayerBasicInfo, MatchState
from tables import DB_PlayerData
from tables.DB_WillMatch import DB_WillMatchs

matchRouter = web.RouteTableDef()
sqlSession = get_session()

player_id_list = []


@matchRouter.get('/get-match-obj/{server_name}')
async def get_match_obj(req):
    server_name = req.match_info['server_name']
    print('服务器请求数据' + server_name)
    if server_name is not None and server_name:
        with get_session() as sqlSession:
            result = (sqlSession.query(DB_WillMatchs).order_by(desc(DB_WillMatchs.time_match))
                      .filter(DB_WillMatchs.server_name == server_name,
                              DB_WillMatchs.is_cancel == False,
                              DB_WillMatchs.time_match >= datetime.datetime.now() - datetime.timedelta(minutes=5))
                      .limit(1)
                      .first())

            will_match: DB_WillMatchs
            if result:
                will_match = result
                # print(will_match.first_team_player_ids)
                return web.json_response(ControllerResponse.success_response(will_match.to_dict()))
            else:
                return web.json_response(ControllerResponse.error_response(-1, "找不到匹配对局"))
    else:
        return web.json_response(ControllerResponse.error_response(-1, "没有提交服务器名称"))
    pass


@matchRouter.post('/divide_players_to_2_group')
async def divide_players_to_2_group(req):
    data = await req.json()

    data = json.loads(data)

    scores_list = sqlSession.query(DB_PlayerData).filter(DB_PlayerData.playerId.in_(list(data))).order_by(
        desc(DB_PlayerData.rank)).all()
    list_a = []
    for i in scores_list:
        z: DB_PlayerData = i
        pm = PlayerBasicInfo(z.__dict__)
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


@matchRouter.get('/get_server_state')
async def get_server_state(req):
    return Response(text='')
