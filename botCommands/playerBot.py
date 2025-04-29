import json
import random
import uuid
from datetime import datetime

import aiohttp
from khl import Bot, Message, GuildUser
from khl.card import CardMessage, Card, Module, Struct, Element, Types
from sqlalchemy import select, desc

from botCommands.ButtonValueImpl import ESActionType
from config import get_rank_name
from entity.ServerEnum import ServerEnum
from entity.WillMatchType import WillMatchType
from init_db import get_session
from kook.CardHelper import replace_sensitive_words
from kook.ChannelKit import EsChannels, ChannelManager, kim, get_troop_type_image, OldGuildChannel
from kook.Enum.KookTextColorEnum import TextColorEnum
from lib.LogHelper import LogHelper, get_time_str
from lib.SelectMatchData import SelectPlayerMatchData
from lib.ServerGameConfig import get_random_faction_2, GameConfig, MapSequence
from lib.ServerManager import ServerManager
from lib.match_state import PlayerBasicInfo, DivideData, MatchState
from tables import *
from tables.Ban import DB_Ban
from tables.PlayerChangeName import DB_PlayerChangeNames
from tables.PlayerMedal import DB_PlayerMedal
from tables.ScoreLimit import DB_ScoreLimit
from tables.WillMatch import DB_WillMatchs

sqlSession = get_session()
g_channels: EsChannels

selectPlayerData = SelectPlayerMatchData()
map_sequence = MapSequence()


def init(bot: Bot, es_channels: EsChannels):
    global g_channels
    g_channels = es_channels

    @bot.command(name='score_list', case_sensitive=False, aliases=['sl'])
    async def world(msg: Message, *args):
        cm = CardMessage()

        sqlSession = get_session()
        sqlSession.commit()

        t = sqlSession.query(DB_PlayerData).order_by(DB_PlayerData.rank.desc()).limit(10).all()
        # print(t)
        kill_scoreboard = '**积分榜单**'
        for id, k in enumerate(t):
            # player: Player = k
            player_data: DB_PlayerData = k
            kill_scoreboard += f"\n{player_data.playerName}:{player_data.rank}"

        game_scoreboard = '**对局榜单**'
        t = sqlSession.query(DB_PlayerData).order_by(DB_PlayerData.match.desc()).limit(10).all()
        for id, k in enumerate(t):
            player: DB_PlayerData = k
            game_scoreboard += f"\n{player.playerName}:{player.win}"

        c2 = Card(
            Module.Section(
                Struct.Paragraph(
                    3,
                    Element.Text(kill_scoreboard, type=Types.Text.KMD),
                    Element.Text(game_scoreboard, type=Types.Text.KMD),
                    Element.Text(f"**步/骑/弓弩**\n",
                                 type=Types.Text.KMD),
                )
            )
        )
        cm.append(c2)
        await msg.reply(cm)

    @bot.command(name='help', case_sensitive=False, aliases=['h'])
    async def help_x(msg: Message):
        t = f'''    
        /help 或 /h 查看所有指令
        **(font)/admin_help /ah 查看管理员指令(font)[warning]**
        /log_history 或 /l 查看最近10场比赛    
        /score_list 或 /sl 查看分数榜单
        /score 或 /s 查看自己的分数
        **(font)/t 或 /type 修改自己的 第一兵种，第二兵种(font)[warning]**
        /change_name 或 /cn 修改名字
        ##### `匹配指令` #####
        **(font)/ae 美式匹配(font)[success]** 【**(font)只能由管理员启动(font)[info]**】
        **(font)/e 均分匹配(font)[success]** 【**(font)只能由管理员启动(font)[info]**】
        
        不想出现 镜像阵营 可以使用指令 {ChannelManager.get_color_text('/e m', TextColorEnum.danger)} 启动
        
        **(font)/select_mode 选人匹配(font)[info]** 【**(font)只能由管理员启动(font)[info]**】
**(font)/cnm (font)[warning]**【比赛ID】 取消比赛,例如 /cnm 6 【**(font)只能由管理员启动(font)[info]**】

        **(font)注册指令(私聊机器人注册,如果直接私聊机器人，但是无响应，可以先公屏输入/help, 再私聊就可以解决问题)：(font)[danger]**
/v [playerId] [code]  例如 /v 76561198104994845 600860
        '''
        file_path = 'satic/img/reg-1.png'
        img_url = await bot.client.create_asset(file_path)
        await msg.reply(CardMessage(Card(
            Module.Header('指令说明'),
            Module.Section(
                Struct.Paragraph(
                    1,
                    Element.Text(t, type=Types.Text.KMD),
                )
            ),
            Module.Container(Element.Image(src=img_url)),
        )))

    @bot.command(name='log_history', case_sensitive=False, aliases=['l'])
    async def show_player_match_history(msg: Message, *args):
        sqlSession = get_session()
        z = sqlSession.query(DB_Player).filter(DB_Player.kookId == msg.author_id)

        if z.count() == 1:
            player: DB_Player = z.first()
            playerId = player.playerId

            match_history = (sqlSession.query(DB_Matchs).order_by(desc(DB_Matchs.time_match))
                             .filter(DB_Matchs.left_players.contains(playerId)).limit(10)).all()
            cm = CardMessage()
            c7 = Card(
                Module.Header(f'玩家：{player.kookName} PlayerId:{player.playerId}'),
                Module.Divider(),
            )

            for i in match_history:
                match_info: DB_Matchs = i
                if match_info is not None:
                    c7.append(Module.Section(
                        Element.Text(f'ID:{match_info.server_name} [{match_info.time_match}]'),
                        Element.Button('查看比赛记录', value=json.dumps(
                            {'match_id': match_info.get_match_id,
                             'player_id': player.playerId,

                             }))
                    ))

            cm.append(c7)
            await msg.reply(cm)
        else:
            await msg.reply('请先注册，如果不会，可以先输入/h 然后按enter发送消息到指令频道')
        pass

    @bot.command(name='reset_score', case_sensitive=False, aliases=['rs'])
    async def reset_score(msg: Message, *args):
        sqlSession = get_session()
        pass

    @bot.command(name='e', case_sensitive=False, aliases=['e'])
    async def es_start_match(msg: Message, arg: str = ''):
        command_description = """
        开启匹配指令
        n:  表示 不移动玩家，仅用作测试
        m:  表示 不使用config  添加地图池子指令 add_map_pool
        e:  不包括东海
        z:  不启动游戏服务器
        
        /e 2 强制使用2服开始
        /e 3 强制使用3服开始
        /e 4 强制使用4服开始
        """
        if not ChannelManager.is_organization_user(msg.author_id):
            await msg.reply('禁止使用管理员指令')
            return

        is_no_move = False
        is_exclude_es = False
        is_force_use_2 = False
        is_force_use_3 = False
        is_force_use_4 = False
        not_open_server = False
        is_use_map_pool_config = True
        for i in arg:
            if i == 'e':
                is_exclude_es = True
            elif i == 'n':
                is_no_move = True
            elif i == '2':
                is_force_use_2 = True
            elif i == 'z':
                not_open_server = True
            elif i == '1':
                is_force_use_2 = False
                is_force_use_3 = False
            elif i == '3':
                is_force_use_2 = False
                is_force_use_3 = True
            elif i == '4':
                is_force_use_2 = False
                is_force_use_3 = False
                is_force_use_4 = True
            elif i == 'm':
                is_use_map_pool_config = False

        # k: PublicVoiceChannel = await bot.client.fetch_public_channel(OldGuildChannel.match_wait_channel)
        # k = await k.fetch_user_list()
        k = await es_channels.wait_channel.fetch_user_list()
        for i in k:
            z: GuildUser = i
            # print(z.__dict__)
            # print(convert_timestamp(z.active_time))
            if is_exclude_es:
                if z.id == ChannelManager.es_user_id:
                    k.remove(z)

        # ####################### 检查人数 #######################
        number_of_user = len(k)
        # if number_of_user % 2 == 1 or number_of_user == 0 or number_of_user != 12:
        #     await msg.reply(f'人数异常, 当前人数为 {len(k)} , 必须为12个人')
        #     return

        sqlSession = get_session()
        z = sqlSession.query(DB_Player).filter(DB_Player.kookId.in_([i.id for i in k])).all()
        dict_for_kook_id = {}
        for i in z:
            t: DB_Player = i
            dict_for_kook_id[t.kookId] = t

        # ####################### 检查封印玩家 #######################
        try:
            ban_player_kook_id = sqlSession.execute(
                select(DB_Ban.kookId).where(DB_Ban.endAt > datetime.now())).scalars().all()
            print(ban_player_kook_id)
            for i in ban_player_kook_id:
                print(i)
                if i in dict_for_kook_id:
                    player_x_ban: DB_Player = dict_for_kook_id[i]
                    await msg.reply(f'有被封印玩家 {player_x_ban.kookName} (met){player_x_ban.kookId}(met) 停止匹配')
                    return
        except Exception as e:
            print(e)

        # ####################### 检查注册玩家，未注册的要移出语音频道 #######################
        # print('this is z data')
        # print([i.__dict__ for i in z])
        # print('this is dict_for_kook_id')
        # print([i.__dict__ for i in dict_for_kook_id.values()])
        player_list = []
        try:
            for id, user in enumerate(k):
                t: GuildUser = user
                if t.id not in dict_for_kook_id:
                    await es_channels.command_channel.send(f'(met){t.id}(met) 你没有注册，请先注册')
                    await move_a_to_b_ex(OldGuildChannel.match_set_channel, [t.id])
                player: DB_Player = dict_for_kook_id[t.id]
                px: DB_PlayerData = sqlSession.query(DB_PlayerData).filter(
                    DB_PlayerData.playerId == player.playerId).first()
                if px is None:
                    px = DB_PlayerData()
                    px.playerId = player.playerId
                    px.playerName = player.kookName
                    px.rank = 1000
                    sqlSession.add(px)
                    sqlSession.commit()

                player_info = PlayerBasicInfo({'username': player.kookName})
                player_info.score = px.rank  # 分数采用总分评价
                player_info.user_id = player.kookId
                player_info.username = player.kookName
                player_info.player_id = player.playerId
                # print(player_info.username)
                player_list.append(player_info)

        except Exception as e:
            print(repr(e))
            LogHelper.log(f"没有注册 {t.id} {t.username}")
            await es_channels.command_channel.send(f'(met){t.id}(met) 你没有注册，请先注册 Exception!')
            await move_a_to_b_ex(ChannelManager.match_set_channel, [t.id])
            return

        # if len(player_list) < 12:
        #     await msg.reply(f'注册人数不足12，请大伙先注册，/help可以提供支持')
        #     return
        # 说明注册人数 >=12
        #     player_list.pop()
        # 2服
        # sqlSession.query(DB_WillMatchs)
        use_server_x = ServerEnum.Server_1
        if is_force_use_2:
            use_server_x = ServerEnum.Server_2
        else:
            use_server_x = ServerEnum.Server_1

        # ############################ 寻找服务器 #############################
        # 定义匿名函数
        count_will_matchs = lambda session, name: (session.query(DB_WillMatchs).order_by(desc(DB_WillMatchs.time_match))
                                                   .filter(DB_WillMatchs.server_name == name,
                                                           DB_WillMatchs.is_cancel == 0,
                                                           DB_WillMatchs.is_finished == 0,
                                                           )).limit(1).count()

        for server in ServerEnum:
            current_server_name_str = ServerManager.getServerName(server)
            result = count_will_matchs(sqlSession, current_server_name_str)
            if result == 0:
                use_server_x = server
                LogHelper.log(f'server result: {use_server_x} {result}')
                break
        else:
            await msg.reply('暂无服务器，请稍等')
            return

        # result = (sqlSession.query(DB_WillMatchs).order_by(desc(DB_WillMatchs.time_match))
        #           .filter(DB_WillMatchs.server_name == name_x_initial,
        #                   DB_WillMatchs.is_cancel == 0,
        #                   DB_WillMatchs.is_finished == 0,
        #                   )).limit(1).count()
        # 当前服务器名字
        # current_server_name_str = ServerManager.getServerName(ServerEnum.Server_1)
        # LogHelper.log('name_x_initial: ' + current_server_name_str)
        # server_1_result = count_will_matchs(sqlSession, current_server_name_str)
        # if server_1_result == 0:
        #     use_server_x = ServerEnum.Server_1
        #     LogHelper.log(f'first_result {use_server_x} {server_1_result}')
        #     pass
        # elif server_1_result > 0:
        #     use_server_x = ServerEnum.Server_2
        #     current_server_name_str = ServerManager.getServerName(use_server_x)
        #     result = count_will_matchs(sqlSession, current_server_name_str)
        # result = (sqlSession.query(DB_WillMatchs).order_by(desc(DB_WillMatchs.time_match))
        #           .filter(DB_WillMatchs.server_name == current_server_name_str,
        #                   DB_WillMatchs.is_cancel == 0,
        #                   DB_WillMatchs.is_finished == 0,
        #                   )).limit(1).count()
        # if result == 0:
        #     use_server_x = ServerEnum.Server_2
        #     LogHelper.log(f'server result: {use_server_x} {result}')
        # if result > 0:
        #     current_server_name_str = ServerManager.getServerName(ServerEnum.Server_3)
        #     result = count_will_matchs(sqlSession, current_server_name_str)
        #     # result = (sqlSession.query(DB_WillMatchs).order_by(desc(DB_WillMatchs.time_match))
        #     #           .filter(DB_WillMatchs.server_name == current_server_name_str,
        #     #                   DB_WillMatchs.is_cancel == 0,
        #     #                   DB_WillMatchs.is_finished == 0,
        #     #                   )).limit(1).count()
        #     if result == 0:
        #         use_server_x = ServerEnum.Server_3
        #         LogHelper.log(f'server result: {use_server_x} {result}')
        #     else:
        #         await msg.reply('暂无服务器，请稍等')
        #         return

        # ############################ 寻找服务器 （→） #############################

        z_config = sqlSession.query(DB_ScoreLimit).filter(DB_ScoreLimit.score_type == 'default').first()
        # name_x = 'CN_BTL_SHAOXING_6'
        if z_config is not None:
            z_config_scre: DB_ScoreLimit = z_config
            # name_x = 'CN_BTL_SHAOXING_6' if z_config_scre.BaseServerName is None else z_config_scre.BaseServerName

        divide_data: DivideData = MatchState.divide_player_ex(player_list)

        will_match_data = DB_WillMatchs()
        will_match_data.time_match = datetime.now()
        will_match_data.match_id = str(uuid.uuid1())
        will_match_data.set_first_team_player_ids(divide_data.get_first_team_player_ids())
        will_match_data.set_second_team_player_ids(divide_data.get_second_team_player_ids())

        first_faction, second_faction = get_random_faction_2()
        will_match_data.first_team_culture = first_faction
        will_match_data.second_team_culture = second_faction

        # 比赛类型，3v3？
        will_match_data.match_type = WillMatchType.get_match_type_with_player_num(len(divide_data.first_team))
        will_match_data.is_cancel = False
        will_match_data.is_finished = False
        will_match_data.map_name = map_sequence.get_next_map()  # ############## 使用图序确定图名

        # will_match_data.server_name = 'CN_BTL_SHAOXING_' + str(use_server_x.value[0])
        # will_match_data.server_name = ServerManager.getServerName(use_server_x)

        if is_force_use_2:
            use_server_x = ServerEnum.Server_2
        elif is_force_use_3:
            use_server_x = ServerEnum.Server_3
        # will_match_data.server_name = 'CN_BTL_SHAOXING_' + str(use_server_x.value[0])
        will_match_data.server_name = ServerManager.getServerName(use_server_x)

        # 获取今天的日期并设置时间为 00:00:00 从而实现 0点充值 比赛id
        # 所有服务器中的比赛ID都是 唯一的
        today_midnight = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        # 更新session
        result_temp = len(sqlSession.execute(
            select(DB_WillMatchs).where(DB_WillMatchs.time_match >= today_midnight)).all())
        newest_data = sqlSession.execute(
            select(DB_WillMatchs).where(DB_WillMatchs.time_match >= today_midnight).order_by(
                desc(DB_WillMatchs.time_match)).limit(1)).first()

        last_match_number = random.randint(3, 6)
        if newest_data is not None and len(newest_data) > 0:
            last_match_number += newest_data[0].match_id_2

        will_match_data.match_id_2 = last_match_number

        try:
            sqlSession.add(will_match_data)
            sqlSession.commit()
        except Exception as e:
            print(e.with_traceback())
            sqlSession.rollback()
            return
            # print(divide_data.attacker_list)
        # print(divide_data.defender_list)
        first_faction, second_faction = get_random_faction_2()
        # print('first_faction', first_faction)
        # print(ChannelManager.get_faction_image(first_faction))
        await msg.reply(CardMessage(
            Card(
                Module.Header(f'服务器: {will_match_data.server_name}-{will_match_data.match_id_2}'),
                Module.Divider(),
                Module.Header('分队情况表'),
                Module.Divider(),
                Module.Header(f'时间:{get_time_str()}'),
                Module.Divider(),
                Module.Section(f'地图名`{will_match_data.map_name}`'),
                Module.Divider(),
                Module.ImageGroup(
                    Element.Image(src=ChannelManager.get_faction_image(first_faction)),
                    Element.Image(src=ChannelManager.image_vs, alt='VS'),
                    Element.Image(src=ChannelManager.get_faction_image(second_faction)),
                ),
                Module.Divider(),
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(divide_data.get_attacker_names(), type=Types.Text.KMD),
                        Element.Text(divide_data.get_attacker_scores(), type=Types.Text.KMD),
                        Element.Text(f'game_info\n{first_faction}', type=Types.Text.KMD),
                    )
                ),
                Module.Divider(),
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(divide_data.get_defender_names(), type=Types.Text.KMD),
                        Element.Text(divide_data.get_defender_scores(), type=Types.Text.KMD),
                        Element.Text(f'game_info\n{second_faction}', type=Types.Text.KMD),
                    )
                ),
                Module.Divider(),
                # Module.Header(f'服务器: {will_match_data.server_name}'),
                # Module.Divider(),
                Module.Section(
                    Element.Text(f'比赛ID：{will_match_data.match_id_2}'),
                    Element.Button(text='取消比赛',
                                   value=json.dumps({'type': ESActionType.Admin_Cancel_Match,
                                                     'match_id_2': will_match_data.match_id_2,
                                                     'match_id': will_match_data.match_id,
                                                     }),
                                   theme=Types.Theme.INFO)
                )
            )
        ))

        # ################################################################ 发送到其他服务器
        if use_server_x in [ServerEnum.Server_3, ServerEnum.Server_4]:
            # 如果服务器 为3，4 需要发送到 另一个服务器
            # requests.post('http://localhost:14725/send_match_info', json=will_match_data)
            async with aiohttp.ClientSession() as session:
                async with session.post('http://localhost:14725/send_match_info',
                                        json=will_match_data.to_dict()) as response:
                    text = await response.text()
            not_open_server = True  # 3服要交给其他服务器启动，因此不需要
            pass

        # ################################################################ 是否移动玩家
        if not is_no_move:
            channel_a, channel_d = OldGuildChannel.get_match_channels(use_server_x)
            await move_a_to_b_ex(channel_a, divide_data.attacker_list)
            await move_a_to_b_ex(channel_d, divide_data.defender_list)
            # if use_server_x == ServerEnum.Server_1:
            #     await move_a_to_b_ex(channel_a, divide_data.attacker_list)
            #     await move_a_to_b_ex(channel_d, divide_data.defender_list)
            # elif use_server_x == ServerEnum.Server_2:
            #     await move_a_to_b_ex(OldGuildChannel.match_attack_channel_2, divide_data.attacker_list)
            #     await move_a_to_b_ex(OldGuildChannel.match_defend_channel_2, divide_data.defender_list)
            # elif use_server_x in [ServerEnum.Server_3, ServerEnum.Server_4]:
            #     await move_a_to_b_ex(OldGuildChannel.match_attack_channel_3, divide_data.attacker_list)
            #     await move_a_to_b_ex(OldGuildChannel.match_defend_channel_3, divide_data.defender_list)
            #     pass
        else:
            LogHelper.log("不移动玩家")

        # ################################################################ 获取 txt配置文件路径
        px = ServerManager.CheckConfitTextFile(use_server_x)
        # px = r'C:\Users\Administrator\Desktop\server files license\Modules\Native\blmm_6_x.txt'
        print('txt file path' + px)
        with open(px, 'w') as f:
            text = GameConfig(server_name=f'CN_BTL_SHAOXING_{use_server_x.value}',
                              match_id=f'{will_match_data.match_id_2}',
                              map_name=will_match_data.map_name,
                              use_map_pool=is_use_map_pool_config)
            text.culture_team1 = first_faction
            text.culture_team2 = second_faction
            f.write(text.to_str())

        # ################################################################ ServerManager.RestartBLMMServer(6)
        if not not_open_server:
            ServerManager.RestartBLMMServerEx(use_server_x)
        else:
            await msg.reply('3,4服，发放至其他服务器')

        await msg.reply('分配完毕!')

    async def move_a_to_b(a: str, b: str):
        channel = await bot.client.fetch_public_channel(a)
        channel_b = await bot.client.fetch_public_channel(b)
        k = await channel.fetch_user_list()
        for id, user in enumerate(k):
            d: GuildUser = user
            await channel_b.move_user(ChannelManager.match_wait_channel, d.id)

    async def move_a_to_b_ex(b: str, list_player: list):
        channel_b = await bot.client.fetch_public_channel(b)
        for id, user_id in enumerate(list_player):
            await channel_b.move_user(b, user_id)

    @bot.command(name='add_change_name_times', case_sensitive=False, aliases=['add_cname_times'])
    async def add_change_name_times(msg: Message, kook_id: str, times: str):
        """
        添加改名次数
        """
        if not ChannelManager.is_es(msg.author_id):
            await msg.reply('禁止使用es指令')
            return

        if kook_id == '' or kook_id is None:
            await msg.reply('kook_id异常')
            return

        if not times.isdigit():
            await msg.reply('没有输入次数')
            return

        # ############################ 检查注册
        session = get_session()
        player: DB_Player = session.query(DB_Player).filter(DB_Player.kookId == kook_id).first()
        if player is None:
            await msg.reply(f'该用户 {ChannelManager.get_at(kook_id)}未注册')
            return

        player_change_names_obj = sqlSession.query(DB_PlayerChangeNames).filter(
            DB_PlayerChangeNames.kookId == kook_id).first()
        if not player_change_names_obj:
            player_change_names_obj = DB_PlayerChangeNames()
            player_change_names_obj.kookId = player.kookId
            player_change_names_obj.kookName = player.kookName
            player_change_names_obj.lastKookName = player.kookName
            player_change_names_obj.playerId = player.playerId
            player_change_names_obj.left_times = int(times)

        else:
            player_change_names_obj.left_times = int(times)
        sqlSession.add(player_change_names_obj)
        sqlSession.commit()

        await msg.reply(f'给 {ChannelManager.get_at(kook_id)}添加了 {times} 改名次数')
        return

    @bot.command(name='change_name', case_sensitive=False, aliases=['cn'])
    async def change_name(msg: Message, new_name: str, *args):
        # 处理玩家随便输入的时候， 在函数原型中加入 , *args
        # sqlSession.commit()
        sqlSession = get_session()
        t: DB_Player = sqlSession.query(DB_Player).filter(DB_Player.kookId == msg.author_id).first()
        if t:
            player: DB_Player = t
            player_change_names_obj = sqlSession.query(DB_PlayerChangeNames).filter(
                DB_PlayerChangeNames.kookId == msg.author_id).first()
            if player_change_names_obj:
                change_names_obj: DB_PlayerChangeNames = player_change_names_obj
                if change_names_obj.left_times > 0:
                    change_names_obj.lastKookName = new_name
                    player.kookName = new_name
                    change_names_obj.left_times -= 1
                    sqlSession.commit()
                    await msg.reply(f'名称更新成功, ->{new_name}, 剩余次数:{change_names_obj.left_times}')
                else:
                    await msg.reply(f'名称更新失败 。 次数用尽')
                    return
                    pass
            else:
                x = DB_PlayerChangeNames()
                x.kookId = player.kookId
                x.kookName = player.kookName
                x.lastKookName = player.kookName
                x.playerId = player.playerId
                sqlSession.add(x)
                sqlSession.commit()
                await msg.reply(f'名称更新失败 。 次数用尽')
        else:
            await msg.reply('你还未注册，该指令不生效')

    @bot.command(name='type', case_sensitive=False, aliases=['t'])
    async def set_player_type(msg: Message, *args):
        c8 = Card(
            Module.Header('第一兵种选择'),
            Module.ActionGroup(
                Element.Button("步兵", value='f1', click=Types.Click.RETURN_VAL, theme=Types.Theme.INFO),
                Element.Button("骑兵", value='f2', click=Types.Click.RETURN_VAL, theme=Types.Theme.DANGER),
                Element.Button("射手", value='f3', click=Types.Click.RETURN_VAL, theme=Types.Theme.SECONDARY)
            ),
            Module.Divider(),
            Module.Header('第二兵种选择'),
            Module.ActionGroup(
                Element.Button("步兵", value='s1', click=Types.Click.RETURN_VAL, theme=Types.Theme.INFO),
                Element.Button("骑兵", value='s2', click=Types.Click.RETURN_VAL, theme=Types.Theme.DANGER),
                Element.Button("射手", value='s3', click=Types.Click.RETURN_VAL, theme=Types.Theme.SECONDARY)
            ),
        )
        await msg.reply(CardMessage(c8))

    @bot.command(name='score', case_sensitive=False, aliases=['s'])
    async def show_score(msg: Message, *args):
        # ####################################### 处理玩家随便输入的时候， 在函数原型中加入 , *args

        sql_session = get_session()

        target_kook_id = msg.author_id
        if len(args) == 1:
            if not ChannelManager.is_admin(msg.author_id):
                await msg.reply('禁止使用管理员参数')
                return
            target_kook_id = str(args[0])

        # ############################### 查询后做了修改要立即提交
        t = sql_session.query(DB_Player).filter(DB_Player.kookId == target_kook_id)

        if t.count() != 1:
            await msg.reply(f"未找到玩家 {ChannelManager.get_at(target_kook_id)} 请先注册")
            return

        player: DB_Player = t.first()

        db_playerdata = sql_session.query(DB_PlayerData).filter(DB_PlayerData.playerId == player.playerId)
        if db_playerdata.count() >= 1:
            db_player: DB_PlayerData = db_playerdata.first()
            player.rank = db_player.rank
        else:
            db_player = player
        sql_session.commit()

        # ######################################### 计算玩家胜率
        target_player_id = player.playerId
        # 查询玩家参与的左侧队伍比赛
        left_matches = sql_session.query(DB_Matchs).filter(DB_Matchs.left_players.contains(target_player_id)).all()
        # 查询玩家参与的右侧队伍比赛
        right_matches = sql_session.query(DB_Matchs).filter(
            DB_Matchs.right_players.contains(target_player_id)).all()

        total_matches = len(left_matches) + len(right_matches)
        win_matches = 0
        draw_matches = 0
        lose_matches = 0

        # 统计左侧队伍比赛的胜利场数和平局场数
        for match in left_matches:
            if match.left_win_rounds > match.right_win_rounds:
                win_matches += 1
            elif match.left_win_rounds == match.right_win_rounds:
                draw_matches += 1
            else:
                lose_matches += 1

        # 统计右侧队伍比赛的胜利场数和平局场数
        for match in right_matches:
            if match.right_win_rounds > match.left_win_rounds:
                win_matches += 1
            elif match.right_win_rounds == match.left_win_rounds:
                draw_matches += 1
            else:
                lose_matches += 1

        if total_matches == 0:
            win_rate = 0
            draw_rate = 0
            lose_rate = 0
        else:
            win_rate = win_matches / total_matches
            draw_rate = draw_matches / total_matches
            lose_rate = lose_matches / total_matches

        db_player.win = win_matches
        db_player.draw = draw_matches
        db_player.lose = lose_matches
        sql_session.commit()
        # ############################## 获取玩家 勋章
        player_medal_db = sql_session.query(DB_PlayerMedal).filter(DB_PlayerMedal.kookId == target_kook_id)
        if player_medal_db.count() == 1:
            player_medal_db: DB_PlayerMedal = player_medal_db.first()
        else:
            player_medal_db = DB_PlayerMedal()
            player_medal_db.playerId = db_player.playerId
            player_medal_db.kookId = player.kookId
            sql_session.add(player_medal_db)
            sql_session.commit()

        cm = CardMessage()
        rank_name = get_rank_name(player.rank)
        c1 = Card(
            Module.Header("基本信息"),
            Module.Context(f'playerId:{player.playerId} kookId:{target_kook_id}'),
            Module.Section(
                Struct.Paragraph(
                    3,
                    Element.Text(
                        f"名字:\n{replace_sensitive_words(player.kookName)}",
                        type=Types.Text.KMD),
                    Element.Text(f"分数:\n{player.rank}", type=Types.Text.KMD),
                    Element.Text(f"位阶:\n(font){rank_name}(font)[pink]",
                                 type=Types.Text.KMD),
                )
            ),
            # ChannelManager.emoji_farmer
            Module.Divider(),
            Module.Section(
                Element.Text(f'(font){rank_name}(font)[pink]({player.rank})', type=Types.Text.KMD),
                Element.Image(src=kim(rank_name), size=Types.Size.LG),
                mode=Types.SectionMode.LEFT
            ),
            Module.Divider(),
            Module.Section(
                Element.Text(f'第(font)一(font)[pink]兵种', type=Types.Text.KMD),
                Element.Image(src=get_troop_type_image(player.first_troop), size=Types.Size.LG),
                mode=Types.SectionMode.LEFT
            ),
            Module.Section(
                Element.Text(f'第(font)2(font)[warning]兵种', type=Types.Text.KMD),
                Element.Image(src=get_troop_type_image(player.second_troop), size=Types.Size.LG),
                mode=Types.SectionMode.LEFT
            )
        )
        Kill_Info = f'''**战场数据**
    击杀:{db_player.kill}
    死亡:{db_player.death}
    助攻:{db_player.assist}
    KDA:{round((db_player.kill + db_player.assist) / max(db_player.death, 1), 3)}
    KD: {round(db_player.kill / max(db_player.death, 1), 3)}
    伤害:{db_player.damage}
    '''

        game_info = f'''**对局数据**
    对局数:{total_matches}
    胜场:{win_matches}
    胜率:{win_rate * 100:.2f}%
    平局:{draw_matches}
    平局率:{draw_rate * 100:.2f}%
    败场:{lose_matches}
    败率:{lose_rate * 100:.2f}%
    胜/败:{round(db_player.win / max(db_player.lose, 1), 3)}
    MVPs:{0}
            '''
        c2 = Card(
            Module.Section(
                Struct.Paragraph(
                    3,
                    Element.Text(Kill_Info, type=Types.Text.KMD),
                    Element.Text(game_info, type=Types.Text.KMD),
                    Element.Text(f"**步/骑/弓弩**\n{db_player.infantry}/{db_player.cavalry}/{db_player.archer}",
                                 type=Types.Text.KMD),
                )
            ),
            Module.Divider(),
            Module.Section(
                Struct.Paragraph(
                    3,
                    Element.Text(player_medal_db.get_testor_emoji)
                )
            )
        )
        # cm.append(c1)
        cm.append(c1)
        cm.append(c2)
        print(repr(cm))
        await msg.reply(cm)
        pass


def convert_timestamp(timestamp):
    from datetime import datetime
    # 将毫秒时间戳转换为秒
    seconds = timestamp / 1000
    # 使用 datetime.fromtimestamp() 将秒级时间戳转换为 datetime 对象
    dt_object = datetime.fromtimestamp(seconds)
    # 格式化 datetime 对象为 24 小时制的字符串
    formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time


if __name__ == '__main__':
    timestamp = 1721137013547
    print(convert_timestamp(timestamp))
