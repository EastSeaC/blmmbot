import json

import aiohttp_jinja2
from aiohttp import web
from aiohttp.web_response import Response
from sqlalchemy import select

from entity.BanType import BanType
from entity.ServerEnum import ServerEnum
from init_db import get_session
from lib.ServerGameConfig import GameConfig
from lib.ServerManager import ServerManager
from tables.Admin import DB_Admin
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


@adminRouter.get('/backup')
def backup_page(request):
    context = {

    }
    return aiohttp_jinja2.render_template('backup_list.html', request, context)


@adminRouter.get('/GetBackUpList')
async def get_backup_list(request):
    import os
    import re
    backup_dir = "C:\\Users\\Administrator\\Desktop\\blmmbackup"
    try:
        if os.path.exists(backup_dir):
            files = os.listdir(backup_dir)
            data = []
            for index, file in enumerate(files):
                # 假设文件名格式为 backup_YYYYMMDD-HHMMSS.json，可根据实际情况修改正则表达式
                match = re.match(r'backup_(\d{8}-\d{6})\.json', file)
                date = match.group(1) if match else ''
                item = {
                    'id': index + 1,
                    'name': file,
                    'date': date
                }
                data.append(item)
            return web.json_response({'code': 0, 'msg': '获取备份列表成功', 'data': data})
        else:
            return web.json_response({'code': 1, 'msg': '备份目录不存在', 'data': []})
    except Exception as e:
        return web.json_response({'code': 2, 'msg': f'获取备份列表失败: {str(e)}', 'data': []})


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


@adminRouter.get('/get-admin-list')
def get_admin_list(req):
    with get_session() as sqlSession:
        z = sqlSession.execute(select(DB_Admin.playerId)).scalars().all()
        return Response(text=json.dumps(z))


@adminRouter.get('/restart_server')
def show_all_window_name(req):
    ServerManager.RestartBLMMServer()
    return Response(text='123')


@adminRouter.get('/test_auto_config')
def test_auto_config(req):
    game_config = GameConfig()
    game_config.ramdom_faction()

    ServerManager.GenerateConfigFile(game_config)
    return Response(text=game_config.to_str())


@adminRouter.get('/test_divide_players')
def test_divide_players(req):
    px = ServerManager.CheckConfitTextFile(ServerEnum.Server_1)
    print(px)
    pass
    return Response(text='1x')


@adminRouter.get('/download_backup_file/{filename}')
async def download_backup_file(request):
    import os
    from aiohttp import web
    filename = request.match_info['filename']
    backup_dir = "C:\\Users\\Administrator\\Desktop\\blmmbackup"
    file_path = os.path.join(backup_dir, filename)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            return web.FileResponse(file_path)
        except Exception as e:
            return web.json_response({'code': 3, 'msg': f'下载文件失败: {str(e)}'})
    else:
        return web.json_response({'code': 4, 'msg': '文件不存在'})
