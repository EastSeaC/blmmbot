import datetime
import json
from asyncio import Queue

from aiohttp import web
from aiohttp.web_response import Response
from sqlalchemy import desc, select

from convert.PlayerMatchData import TPlayerMatchData
from entity.ServerEnum import ServerEnum
from lib.LogHelper import LogHelper, get_midnight_time, get_time_str
from entity.webEntity.ControllerResponse import ControllerResponse
from init_db import get_session
from lib.ScoreMaster import calculate_score
from lib.ServerManager import ServerManager
from lib.match_state import PlayerBasicInfo, MatchState, MatchConditionEx
from tables import DB_PlayerData, DB_Matchs
from tables.WillMatch import DB_WillMatchs

matchRouter = web.RouteTableDef()

player_id_list = []


@matchRouter.get('/get-match-obj/{server_name}')
async def get_match_obj(req):
    server_name = str(req.match_info['server_name'])
    print('服务器请求数据' + server_name)
    if server_name is not None and server_name:
        server_name = server_name if '-' not in server_name else server_name.split('-')[0]
        print(server_name)
        with get_session() as sqlSession:
            result = (sqlSession.query(DB_WillMatchs).order_by(desc(DB_WillMatchs.time_match))
                      .filter(DB_WillMatchs.server_name == server_name,
                              DB_WillMatchs.is_cancel == 0,
                              DB_WillMatchs.time_match >= datetime.datetime.now() - datetime.timedelta(minutes=5))
                      .limit(1)
                      .first())

            will_match: DB_WillMatchs
            if result:
                will_match = result
                # print(will_match.first_team_player_ids)
                return web.json_response(ControllerResponse.success_response(will_match.to_dict()))
            else:
                textresult = "找不到匹配对局"
                print(textresult)
                return web.json_response(ControllerResponse.error_response(-1, textresult))
    else:
        return web.json_response(ControllerResponse.error_response(-1, "没有提交服务器名称"))
    pass


@matchRouter.get('/cancel-match/{server_name}/{match_id}')
async def cancel_match(req):
    server_name = req.match_info['server_name']
    match_id = req.match_info['match_id']

    LogHelper.log('尝试取消比赛')
    sql_session = get_session()
    if server_name is not None and match_id is not None:
        server_name = server_name.split('-')[0]
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
            will_match.is_cancel = True
            will_match.cancel_reason = f'管理员于{get_time_str()}取消'
            try:
                sql_session.add(will_match)
                sql_session.commit()
                LogHelper.log('取消比赛成功')
                return ControllerResponse.success_response(True)
            except Exception as e:
                sql_session.rollback()
                return ControllerResponse.error_response(-1, "ServerInternal error")


@matchRouter.get('/is-cancel-match/{server_name}/{match_id}')
async def is_cancel_match(req):
    server_name = req.match_info['server_name']
    match_id = req.match_info['match_id']

    with get_session() as sql_session:
        if server_name is None or match_id is None:
            return web.json_response(text=ControllerResponse.error_response(-1, "未找到对应match"))
        target_match_id = int(match_id)

        today_midnight = get_midnight_time()
        z = sql_session.execute(select(DB_WillMatchs)
        .order_by(desc(DB_WillMatchs.time_match)).where(
            DB_WillMatchs.server_name == server_name,
            DB_WillMatchs.match_id_2 == target_match_id)).scalrs().first()

        if z is None or len(z) == 0:
            return web.json_response(text=ControllerResponse.error_response(-1, "未找到对应match"))
        will_match: DB_WillMatchs = z[0]
        if will_match.is_cancel == 1 or will_match.is_finished == 1:
            return web.json_response(text=ControllerResponse.success_response(True))
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


@matchRouter.post('/send_match_info')
async def send_match_info(req):
    print('测试测试')
    message: Queue = req.app['message_queue']
    data = await req.json()
    print(data)
    print(type(data))
    await message.put(data)
    req.app['message_queue'] = message
    return web.json_response(text='123')


@matchRouter.post('/upload_player_list')
async def upload_player_list(req):
    data = await req.json()

    data = json.loads(data)
    global player_id_list
    player_id_list = list(data)

    LogHelper.log('玩家player ids 上传收到 ')
    return Response(text='123')
    pass


@matchRouter.post('/UploadMatchDataTest')
async def update_match_data2(request):
    formatted_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[UploadMatchData|Right{formatted_time}]")

    data = await request.json()
    print(data)

    print('*' * 45)
    # for key, value in data.items():
    #     print(f"Key: {key}, Value: {value}")
    if not isinstance(data, dict):
        data = json.loads(data)
    match_data = DB_Matchs()
    match_data.left_scores = data["AttackScores"]
    match_data.right_scores = data["DefendScores"]
    match_data.left_players = list(set(data["AttackPlayerIds"]))
    match_data.right_players = list(set(data["DefendPlayerIds"]))
    match_data.left_win_rounds = data["AttackRound"]
    match_data.right_win_rounds = data["DefendRound"]
    match_data.server_name = data["ServerName"]
    match_data.tag = data["Tag"]
    playerData = data["_players"]
    match_data.player_data = playerData
    match_data.raw = data

    # #### 提前保存，防止数据异常 ####

    print('解析前的tag', match_data.tag, type(match_data.tag))
    if isinstance(match_data.tag, dict):
        match_data.tag = json.dumps(match_data.tag)
        print('属性判定', isinstance(match_data.tag, dict))
    session = get_session()
    session.add(match_data)
    # session.commit()
    session.rollback()

    match_data.tag = json.loads(match_data.tag)
    if isinstance(match_data.tag, dict):
        is_match_ending = match_data.tag["IsMatchEnding"]
        round_count = int(match_data.tag["RoundCount"])
    else:
        round_count = 0
        is_match_ending = False
    if round_count < 3:
        LogHelper.log("未满3局")
        return
    if isinstance(match_data.tag, dict):
        match_data.tag = json.dumps(match_data.tag)
    # session.add(t)
    player_ids = list(playerData.keys())
    print(type(player_ids))
    print(player_ids)

    """
    保存数据
    """

    playerData_2: dict = playerData
    print('*' * 65)

    show_data = []
    team_a_data = []
    team_b_data = []
    player_score_dict = {}

    # 搜索玩家数据
    result = session.query(DB_PlayerData).filter(DB_PlayerData.playerId.in_(player_ids))

    result_player_ids = []
    for i in result:
        oldData: DB_PlayerData = i
        result_player_ids.append(oldData.playerId)
    #     找到之前没有数据的玩家
    missing_data = [value for key, value in playerData.items() if key not in result_player_ids]

    match_total_sum = match_data.get_total_data
    for i in result:
        oldData: DB_PlayerData = i
        k = TPlayerMatchData(playerData[oldData.playerId])
        ## 计分系统
        # print(f"{k.player_id}: {k.win_rounds}")
        if not k.is_spectator_by_score():
            k.set_old_score(oldData.rank)

            if match_total_sum.attacker_rounds < match_total_sum.defender_rounds:
                if k.player_id in match_data.left_players:
                    print(
                        f"{k.player_name} .分数{match_total_sum.attacker_rounds}-{match_total_sum.defender_rounds}，false")
                    k.set_is_lose(True)
                elif k.player_id in match_data.right_players:
                    print(
                        f"{k.player_name} .分数{match_total_sum.attacker_rounds}-{match_total_sum.defender_rounds}，win")
                    k.set_is_lose(False)
            elif match_total_sum.attacker_rounds == match_total_sum.defender_rounds:
                print(f"{k.player_name} .分数{match_total_sum.attacker_rounds}-{match_total_sum.defender_rounds}")
                if k.player_id in match_data.left_players or k.player_id in match_data.right_players:
                    k.set_is_lose(False)
            elif match_total_sum.attacker_rounds > match_total_sum.defender_rounds:
                if k.player_id in match_data.left_players:
                    print(
                        f"{k.player_name} .分数{match_total_sum.attacker_rounds}-{match_total_sum.defender_rounds}，win")
                    k.set_is_lose(False)
                elif k.player_id in match_data.right_players:
                    print(
                        f"{k.player_name} .分数{match_total_sum.attacker_rounds}-{match_total_sum.defender_rounds}，false")
                    k.set_is_lose(True)
            # if k.win_rounds >= 3 or k.win >= 3:
            #     k.set_is_lose(False)
            # else:
            #     k.set_is_lose(True)
            sum_score, score_dict = calculate_score(match_total_sum, k)
            oldData.rank += sum_score
            player_score_dict[k.player_id] = score_dict

            k.set_new_score(oldData.rank)
            show_data.append(k)

            if k.player_id in match_data.left_players:
                team_a_data.append(k)
            else:
                team_b_data.append(k)
        else:
            LogHelper.log("跳过")

        oldData.add_match_data(k)
        # print(f"{oldData.rank}")
        oldData.playerName = k.player_name

    for i in missing_data:
        # print('test123')
        k = TPlayerMatchData(i)
        # print(k.__dict__)
        newData = DB_PlayerData()
        newData.clear_data()
        newData.playerId = k.player_id
        newData.playerName = k.player_name
        # 积分
        k.set_old_score(newData.rank)
        if not k.is_spectator_by_score():
            if k.player_id in match_data.left_players:
                if match_total_sum.attacker_rounds < match_total_sum.defender_rounds:
                    k.set_is_lose(True)
                else:
                    k.set_is_lose(False)
            elif k.player_id in match_data.right_players:
                if match_total_sum.attacker_rounds > match_total_sum.defender_rounds:
                    k.set_is_lose(False)
                else:
                    k.set_is_lose(True)

            sum_score, score_dict = calculate_score(match_total_sum, k)
            newData.rank += sum_score

            player_score_dict[k.player_id] = score_dict

            k.set_new_score(newData.rank)
            show_data.append(k)

            if k.player_id in match_data.left_players:
                team_a_data.append(k)
            elif k.player_id in match_data.left_players:
                team_b_data.append(k)

        # 积分
        newData.add_match_data(k)

        session.add(newData)
    pass

    match_data.player_scores = json.dumps(player_score_dict)
    # session.commit()
    session.rollback()

    # ################################### 设置比赛结束
    server_name = ServerManager.getServerName(ServerEnum.Server_1)
    server_name_withou_clear: str = match_data.server_name
    if '-' in server_name_withou_clear:
        server_name_withou_clear = server_name_withou_clear.split('-')[0]
    z = session.query(DB_WillMatchs).filter(DB_WillMatchs.server_name == server_name_withou_clear,
                                            DB_WillMatchs.match_id_2 == match_data.get_match_id)
    if z.count() > 0:
        for i in z:
            db_x: DB_WillMatchs = i
            db_x.is_finished = 1

            session.merge(db_x)
        # session.commit()
        session.rollback()

    # (session.query(DB_WillMatchs).filter(DB_WillMatchs.match_id_2 == )
    # 保存数据到静态 , 转为有比赛结果
    MatchConditionEx.server_name = match_data.server_name
    MatchConditionEx.round_count = round_count
    MatchConditionEx.data = show_data
    MatchConditionEx.data2 = team_a_data + team_b_data
    MatchConditionEx.attacker_score = match_data.left_win_rounds
    MatchConditionEx.defender_score = match_data.right_win_rounds
    if is_match_ending:
        # 存放到 静态类中，让机器人输出
        MatchConditionEx.end_game = True
    LogHelper.log("数据已保存")

    return web.Response(text='123')
