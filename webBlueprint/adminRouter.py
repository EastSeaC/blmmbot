from aiohttp import web
from aiohttp.web_response import Response

from lib.ServerManager import ServerManager

adminRouter = web.RouteTableDef()


@adminRouter.get('/show_all_window_name')
def show_all_window_name(req):
    ServerManager.RestartBLMMServer()
    return Response(text='123')
