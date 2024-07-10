import json

import aiohttp_jinja2
from aiohttp import web
from aiohttp.web_response import Response

from entity.BanType import BanType
from init_db import get_session
from lib.ServerManager import ServerManager
from match_state import PlayerInfo
from tables.Ban import DB_Ban

adminRouter = web.RouteTableDef()
sqlSession = get_session()


@adminRouter.get('/debug')
def p(request):
    context = {

    }
    return aiohttp_jinja2.render_template('debug.html', request, context)


@adminRouter.get('/ban')
def p2(request):
    context = {

    }
    return aiohttp_jinja2.render_template('ban.html', request, context)


@adminRouter.get('/ban_player_with_kook_id/{kookId}')
def ban_player(request):
    kook_id = request.match_info['kookId']

    ban_obj = DB_Ban()
    ban_obj.kookId = kook_id
    ban_obj.banType = BanType.ForbiddenJoinChannel
    sqlSession.add(ban_obj)
    sqlSession.commit()

    z = json.dumps({'state': True})
    return Response(text=z)


@adminRouter.get('/show_all_window_name')
def show_all_window_name(req):
    ServerManager.RestartBLMMServer()
    return Response(text='123')


@adminRouter.get('/test_divide_players')
def test_divide_players(req):
    pass
    return Response(text='1x')
