from aiohttp import web
from aiohttp.web_response import Response

from lib.ServerManager import ServerManager
from match_state import PlayerInfo

adminRouter = web.RouteTableDef()


@adminRouter.get('/show_all_window_name')
def show_all_window_name(req):
    ServerManager.RestartBLMMServer()
    return Response(text='123')


@adminRouter.get('/test_divide_players')
def test_divide_players(req):

    pass
    return Response(text='1x')
