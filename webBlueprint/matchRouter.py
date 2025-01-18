import datetime
import json

from aiohttp import web
from aiohttp.web_response import Response
from sqlalchemy import desc, select

from lib.LogHelper import LogHelper, get_midnight_time, get_time_str
from entity.webEntity.ControllerResponse import ControllerResponse
from init_db import get_session
from lib.match_state import PlayerBasicInfo, MatchState
from tables import DB_PlayerData
from tables.DB_WillMatch import DB_WillMatchs

matchRouter = web.RouteTableDef()

player_id_list = []


@matchRouter.get('/get-match-obj/{server_name}')
async def get_match_obj(req):
    server_name = str(req.match_info['server_name'])
    print('服务器请求数据' + server_name)
    if server_name is not None and server_name:
        server_name = server_name if '-' not in server_name else server_name.split('-')[0]
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


@matchRouter.get('/cancel-match/{server_name}/{match_id}')
async def cancel_match(req):
    server_name = req.match_info['server_name']
    match_id = req.match_info['match_id']

    sql_session = get_session()
    if server_name is not None and match_id is not None:
        target_match_id = int(match_id)

        today_midnight = get_midnight_time()
        z = sql_session.execute(select(DB_WillMatchs).where(DB_WillMatchs.time_match >= today_midnight,
                                                            DB_WillMatchs.match_id_2 == target_match_id)).first()
        if z is None or len(z) == 0:
            return ControllerResponse.success_response(True)
        will_match: DB_WillMatchs = z[0]
        if will_match.is_cancel is True or will_match.is_finished is True:
            return ControllerResponse.success_response(True)
        else:
            will_match.is_cancel = True
            will_match.cancel_reason = f'管理员于{get_time_str()}取消'
            try:
                sql_session.add(will_match)
                sql_session.commit()
                return ControllerResponse.success_response(True)
            except Exception as e:
                sql_session.rollback()
                return ControllerResponse.error_response(-1, "ServerInternal error")


@matchRouter.get('/is-cancel-match/{server_name}/{match_id}')
async def is_cancel_match(req):
    server_name = req.match_info['server_name']
    match_id = req.match_info['match_id']

    sql_session = get_session()
    if server_name is not None and match_id is not None:
        target_match_id = int(match_id)

        today_midnight = get_midnight_time()
        z = sql_session.execute(select(DB_WillMatchs).where(DB_WillMatchs.time_match >= today_midnight,
                                                            DB_WillMatchs.server_name == server_name,
                                                            DB_WillMatchs.match_id_2 == target_match_id)).first()
        if z is None or len(z) == 0:
            return ControllerResponse.success_response(True)
        will_match: DB_WillMatchs = z[0]
        if will_match.is_cancel is True or will_match.is_finished is True:
            return ControllerResponse.success_response(True)
        else:
            return ControllerResponse.success_response(False)


@matchRouter.post('/divide_players_to_2_group')
async def divide_players_to_2_group(req):
    data = await req.json()

    data = json.loads(data)
    sqlSession = get_session()
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
