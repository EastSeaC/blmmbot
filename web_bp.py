import json
from datetime import datetime, timedelta
from io import BytesIO
from random import randint

import aiohttp_jinja2
from aiohttp import web
from aiohttp.web import Response
from openpyxl.workbook import Workbook
from sqlalchemy import or_

from LogHelper import LogHelper
from convert.PlayerMatchData import TPlayerMatchData
from init_db import get_session
from tables import *

# 创建一个蓝图
bp = web.RouteTableDef()

# 定义处理程序
session = get_session()


def generate_numeric_code(length=6):
    return ''.join([str(randint(0, 9)) for _ in range(length)])


@bp.get('/')
async def index(request):
    context = {
        'title': 'Main Page',
        'content': 'Welcome to the main page!',
        'match_data': json.dumps([i.get_data() for i in session.query(DB_Matchs).all()])
    }

    return aiohttp_jinja2.render_template('main.html', request, context)


@bp.get('/get_player_info/{player_id}')
async def get_player_info(request):
    player_id = request.match_info['player_id']
    z = session.query(DB_PlayerData).filter(Player.playerId == player_id)
    return z


@bp.get('/get_reg/{player_id}')
async def get_reg(req):
    player_id = req.match_info['player_id']
    session.commit()
    query = session.query(Verify).filter(Verify.playerId == player_id)
    z = query.count()
    very = Verify()
    if z == 0:
        very.code = generate_numeric_code()
        very.playerId = player_id
        session.add(very)
        session.commit()
    elif z == 1:
        very: Verify = query.first()
    LogHelper.log(f"{player_id}, 验证码{very.code}")
    return Response(text=very.code)


@bp.get('/reg/{player_id}/{very_code}')
async def reg_player(request):
    # player_id = request.match_info['player_id']
    # try:
    #     sucess, reson = await add_player_code(player_id)
    # except Exception as e:
    #     sucess = False
    #     reson = str(e)
    # result_text = json.dumps({'success': sucess, 'reason': reson})
    return web.Response(text='not implement')


@bp.get('/GetVerifyCode')
async def get_verify_code(request):
    session.commit()
    result = session.query(Verify).filter(
        Verify.until_time >= datetime.now()).all()
    list = {}
    for i in result:
        u: Verify = i
        list[u.playerId] = u.code
    return web.Response(text=json.dumps(list))


# @bp.get('/UploadMatchData/{json_str}')
# async def update_match_data(request):
#     print('update_match_data')
#     session.commit()
#
#     json_str = request.match_info['json_str']
#     data = json.loads(json_str)
#     k = json.loads(data)
#     players = k["_players"]
#     all_player_ids = list(players.keys())
#
#     # results = session.query(Player).filter(Player.playerId.in_(all_player_ids)).all()
#     for k, v in players.items():
#         q = session.query(Player).filter(Player.playerId == k)
#         if q.count() == 1:
#             player: Player = q.first()
#
#             player.team_damage += int(float(v["TKValue1"]))
#             player.damage += int(float(v["AttackValue1"]))
#             player.kill += int(v["KillNum1"])
#             player.death += int(v["DeadNum1"])
#
#     session.commit()


@bp.post('/UploadMatchData')
async def update_match_data2(request):
    formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[UploadMatchData|Right{formatted_time}]")
    data = await request.json()
    for key, value in data.items():
        print(f"Key: {key}, Value: {value}")

    session.commit()
    t = DB_Matchs()
    t.left_scores = data["AttackScores"]
    t.right_scores = data["DefendScores"]
    t.left_players = data["AttackPlayerIds"]
    t.right_players = data["DefendPlayerIds"]
    t.left_win_rounds = data["AttackRound"]
    t.right_win_rounds = data["DefendRound"]
    t.server_name = data["ServerName"]
    t.tag = data["Tag"]
    playerData = data["_players"]
    t.raw = playerData

    session.add(t)

    result = session.query(DB_PlayerData).filter(DB_PlayerData.playerId.in_(playerData.keys())).all()
    result_player_ids = []
    for i in result:
        oldData: DB_PlayerData = i
        result_player_ids.append(oldData.playerId)
    missing_data = [value for key, value in playerData.items() if key not in result_player_ids]

    # print('u0', playerData.keys(), result)
    for i in result:
        # print('u2')
        oldData: DB_PlayerData = i
        k = TPlayerMatchData(playerData[oldData.playerId])

        oldData.playerName = k.player_name
        oldData.match += 1
        oldData.win += k.win
        oldData.lose += k.lose
        oldData.draw += k.draw_rounds

        oldData.infantry += k.Infantry
        oldData.cavalry += k.Cavalry
        oldData.archer += k.Archer

        oldData.damage += k.damage
        oldData.team_damage += k.team_damage

        oldData.win_rounds += k.win_rounds
        oldData.fail_rounds += k.lose_rounds
        oldData.draw_rounds += k.draw_rounds

        oldData.horse_damage += k.horse_damage

        oldData.kill += k.kill
        oldData.death += k.death
        oldData.assist += k.assist
        # oldData.horse_kill+=k.ho

    for i in missing_data:
        # print('test123')
        k = TPlayerMatchData(i)
        newData = DB_PlayerData()

        newData.playerId = k.player_id
        newData.playerName = k.player_name
        newData.match = 1

        newData.infantry = k.Infantry
        newData.cavalry = k.Cavalry
        newData.archer = k.Archer

        newData.damage = k.damage
        newData.team_damage = k.team_damage

        newData.win_rounds = k.win_rounds
        newData.fail_rounds = k.lose_rounds
        newData.draw_rounds = k.draw_rounds

        newData.horse_damage = k.horse_damage

        newData.kill = k.kill
        newData.death = k.death
        newData.assist = k.assist

        session.add(newData)
    pass

    session.commit()

    return web.Response(text='123')


@bp.get('/GetData')
async def GetData(request):
    # 创建一个Excel文件
    wb = Workbook()
    ws = wb.active

    one_hour_ago = datetime.now() - timedelta(hours=1)

    session.commit()
    latest_record = session.query(DB_Matchs).filter(
        DB_Matchs.time_match >= one_hour_ago,
    ).first()

    latest_match_data: DB_Matchs = latest_record
    print(latest_match_data)
    if latest_match_data is None:
        return web.Response(text='Data out dated')

    p = latest_match_data.raw
    # 找到 一小时内，含有相同玩家的所有记录
    all_player_ids = list(p.keys())
    some_records = session.query(DB_Matchs).filter(
        DB_Matchs.time_match >= one_hour_ago,
        or_(*[DB_Matchs.raw.like(f'%{s}%') for s in all_player_ids])
    )

    player_record = {}
    for record in some_records:
        match_data: DB_Matchs = record
        t = match_data.raw
        for k, v in t.items():
            u = TPlayerMatchData(v)
            if k not in player_record:
                player_record[k] = u
            else:
                old_data: TPlayerMatchData = player_record[k]
                if old_data.player_name is None:
                    old_data.player_name = u.player_name
                old_data.kill += u.kill
                old_data.death += u.death
                old_data.assist += u.assist
                old_data.win_rounds += u.win_rounds
                old_data.lose_rounds += u.lose_rounds
                old_data.damage += u.damage
                old_data.team_damage += u.team_damage
                old_data.horse_damage += u.horse_damage
                old_data.horse_tk += u.horse_damage

                player_record[k] = old_data
        pass

    ws.append(DB_PlayerData.GetHeaders)
    for key, record in player_record.items():
        record2: TPlayerMatchData = record
        ws.append(record2.get_data_list)

    # 美化
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 20

    # 将Excel文件内容写入BytesIO对象
    excel_data = BytesIO()
    wb.save(excel_data)
    excel_data.seek(0)

    # 设置响应头信息
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers[
        'Content-Disposition'] = f'attachment; filename="{datetime.now().strftime("%m-%d-%H-%M-%S")}BTL.xlsx"'

    # 将BytesIO对象中的内容作为响应返回
    await response.prepare(request)
    await response.write(excel_data.read())

    return response


@bp.post('/GetDataEx')
async def GetDataEx(request):
    data = await request.json()
    print(data)
    # 创建一个Excel文件
    wb = Workbook()
    ws = wb.active
    ws.title = '玩家数据'
    session.commit()
    some_records = session.query(DB_Matchs).filter(
        DB_Matchs.id.in_(data)
    ).all()

    player_record = {}
    for record in some_records:
        match_data: DB_Matchs = record
        t = match_data.raw
        for k, v in t.items():
            u = TPlayerMatchData(v)
            if k not in player_record:
                player_record[k] = u
            else:
                old_data: TPlayerMatchData = player_record[k]
                if old_data.player_name is None:
                    old_data.player_name = u.player_name
                old_data.kill += u.kill
                old_data.death += u.death
                old_data.assist += u.assist
                old_data.win_rounds += u.win_rounds
                old_data.lose_rounds += u.lose_rounds
                old_data.damage += u.damage
                old_data.team_damage += u.team_damage
                old_data.horse_damage += u.horse_damage
                old_data.horse_tk += u.horse_tk

                player_record[k] = old_data
        pass

    ws.append(DB_PlayerData().GetHeaders())
    for key, record in player_record.items():
        record2: TPlayerMatchData = record
        ws.append(record2.get_data_list)

    # 美化
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 20

    # 附录信息
    new_sheet = wb.create_sheet(title='附录信息')
    new_sheet.apeend(['开始时间', ""])
    new_sheet.apeend(['结束时间', ""])

    # 将Excel文件内容写入BytesIO对象
    excel_data = BytesIO()
    wb.save(excel_data)
    excel_data.seek(0)

    # 设置响应头信息
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers[
        'Content-Disposition'] = f'attachment; filename="{datetime.now().strftime("%m-%d-%H-%M-%S")}BTL.xlsx"'

    # 将BytesIO对象中的内容作为响应返回
    await response.prepare(request)
    await response.write(excel_data.read())

    return response
    pass


# @bp.get('/v/{user_id}/{code}')
# async def validate_player(request):
#     user_id = request.match_info['user_id']
#     code = request.match_info['code']
if __name__ == '__main__':
    t = '''{
        "_players": {
            "2.0.0.76561199044372880": {
                "player_id": "2.0.0.76561199044372880",
                "AttackValue1": 0.0,
                "TKValue1": 0.0,
                "TKTimes1": 0.0,
                "TKPlayerNumbers1": 0.0,
                "AttackHorse1": 0,
                "TKHorse1": 0,
                "KillNum1": 0,
                "DeadNum1": 0
            },
            "2.0.0.76561198157649182": {
                "player_id": "2.0.0.76561198157649182",
                "AttackValue1": 100.0,
                "TKValue1": 0.0,
                "TKTimes1": 0.0,
                "TKPlayerNumbers1": 0.0,
                "AttackHorse1": 0,
                "TKHorse1": 0,
                "KillNum1": 0,
                "DeadNum1": 0
            }
        }
    }
    '''
    k = json.loads(t)
    players = k["_players"]
    for k, v in players.items():
        print(v)
