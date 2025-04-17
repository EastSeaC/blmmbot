import datetime
import json
import random
import uuid

import aiohttp
import requests
from khl import Bot, Message, GuildUser, PublicVoiceChannel
from khl.card import Card, Module, Element, Types, CardMessage, Struct
from sqlalchemy import desc, select

from entity.ServerEnum import ServerEnum
from lib.LogHelper import get_time_str
from entity.WillMatchType import WillMatchType
from kook.ChannelKit import EsChannels, OldGuildChannel
from init_db import get_session
from kook.ChannelKit import ChannelManager
from lib.SelectMatchData import SelectPlayerMatchData
from lib.ServerGameConfig import get_random_faction_2
from lib.ServerManager import ServerManager
from lib.match_state import PlayerBasicInfo, MatchState, DivideData, MatchConditionEx
from tables import *
from tables.DB_WillMatch import DB_WillMatchs

sqlSession = get_session()
g_channels: EsChannels


def init(bot: Bot, es_channels: EsChannels):
    global g_channels
    g_channels = es_channels

    @bot.command(name='uca', case_sensitive=False, aliases=['ca', 'xa'])
    async def worldO(msg: Message, exclude_me: str):
        print("123")
        print(msg.author_id)
        if msg.author_id != ChannelManager.es_user_id:
            await msg.reply('禁止使用es 指令')

            # guild = await bot.client.fetch_guild(ChannelManager.sever)
        wait_channel = await bot.client.fetch_public_channel(ChannelManager.match_wait_channel)
        wait_channel: PublicVoiceChannel = wait_channel
        user_list = await wait_channel.fetch_user_list()
        # for i in user_list:
        #     print(i.id)
        print(f'{[i.id for i in user_list]}')
        if exclude_me == '1':
            print('排除东海')
            user_list = [i for i in user_list if i.id != ChannelManager.es_user_id]

        z = sqlSession.query(DB_Player).filter(DB_Player.kookId.in_([i.id for i in user_list])).all()
        dict_for_kook_id = {}
        for i in z:
            t: DB_Player = i
            dict_for_kook_id[t.kookId] = t

        player_list = []
        for id, user in enumerate(user_list):
            t: GuildUser = user
            if t.id not in dict_for_kook_id:
                print(f'{t.id} no register')
                # await es_channels.command_channel.send(f'(met){t.id}(met) 你没有注册，请先注册')
                # await move_a_to_b_ex(ChannelManager.match_set_channel, [t.id])
            player: DB_Player = dict_for_kook_id[t.id]
            player_info = PlayerBasicInfo({'username': t.username})
            player_info.score = player.rank
            player_info.user_id = t.id
            player_info.username = t.username
            # print(player_info.kook_name)
            player_list.append(player_info)

        if len(player_list) < 12:
            await msg.reply(f'注册人数不足12，请大伙先注册，/help可以提供支持')
        if len(player_list) % 2 != 0:
            await msg.reply(f'人数非奇数！')
            return
        divide_data: DivideData = MatchState.divide_player_ex(player_list)
        await msg.reply(CardMessage(
            Card(
                Module.Header('分队情况表'),
                Module.Divider(),
                Module.Header(f'时间:{get_time_str()}'),
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(divide_data.get_attacker_names(), type=Types.Text.KMD),
                        Element.Text(divide_data.get_attacker_scores(), type=Types.Text.KMD),
                        Element.Text('game_info', type=Types.Text.KMD),
                    )
                ),
                Module.Divider(),
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(divide_data.get_defender_names(), type=Types.Text.KMD),
                        Element.Text(divide_data.get_defender_scores(), type=Types.Text.KMD),
                        Element.Text('game_info', type=Types.Text.KMD),
                    )
                ),
            )
        ))
        # print(divide_data.get_defender_names())
        # r = requests.post(UrlHelper.delete_message,
        #                   headers={
        #                       f'Authorization': f"Bot {config['token']}",
        #                   },
        #                   params={
        #                       'msg_id': '8477c586-9111-4312-bc38-a9664d75b32c',
        #                   })
        # print(r.text)
        # print(UrlHelper.delete_message)
        # z = await es_channels.command_channel.list_messages()

    @bot.command(name='testSelect', case_sensitive=False, aliases=['test-sm'])
    async def test_select(msg: Message, *args):

        # user_list = ['482714005', '1555061634', '755654595', '304648463', '3484257139', '2806603494', '3394658957',
        #              '2806603494', '1384765669', '1510300409', '828555933', '3784439652']
        user_list = ['482714005', '3173112866', '755654595', '304648463', '3484257139', '2806603494', '3394658957',
                     '2806603494', '1384765669', '1510300409', '2977084297', '3167451943']
        first_team_o = '482714005'
        second_team_o = '1555061634'
        remove_team_manager_user_list = [i for i in user_list if i != first_team_o or i != second_team_o]

        with get_session() as z_session:
            z = z_session.execute(select(DB_Player).where(DB_Player.kookId.in_(user_list))).all()
            dict_for_kook_id = {}
            for i in z:
                t: DB_Player = i[0]
                print(f"ZX{t.kookName},{t.rank} ")
                dict_for_kook_id[t.kookId] = t

            player_list = []
            print(dict_for_kook_id)
            for id, user in enumerate(user_list):
                player: DB_Player = dict_for_kook_id[user]
                player_info = PlayerBasicInfo({'username': player.kookName})
                player_info.score = player.rank
                player_info.user_id = player.kookId
                player_info.username = player.kookName
                player_info.player_id = player.playerId
                # print(player_info.username)
                player_list.append(player_info)

            if len(player_list) < 12:
                await msg.reply(f'注册人数不足12，请大伙先注册，/help可以提供支持')
            if len(player_list) % 2 != 0:
                await msg.reply(f'人数非奇数！')
                return
            divide_data: DivideData = MatchState.divide_player_ex(player_list)

            will_match_data = DB_WillMatchs()
            will_match_data.time_match = datetime.datetime.now()
            will_match_data.match_id = str(uuid.uuid1())
            will_match_data.set_first_team_player_ids(divide_data.get_first_team_player_ids())
            # will_match_data.set_second_team_player_ids(divide_data.get_second_team_player_ids())

            first_faction, second_faction = get_random_faction_2()
            will_match_data.first_team_culture = first_faction
            will_match_data.second_team_culture = second_faction

            will_match_data.match_type = WillMatchType.Match88
            will_match_data.is_cancel = False
            will_match_data.is_finished = False
            will_match_data.server_name = 'CN_BTL_NINGBO_1'

            card8 = Card(Module.Header(text='服务器: CN_BTL_NINGBO_1'),
                         Module.Divider(),
                         )
            for i in z:
                t: DB_Player = i[0]
                print(f"{t.kookName},{t.rank} ")
                if t.kookId == first_team_o or t.kookId == second_team_o:
                    continue
                card8.append(Module.Section(
                    Element.Text(
                        f"{t.kookName}({t.rank}) \t {ChannelManager.get_troop_emoji(t.first_troop)} {ChannelManager.get_troop_emoji(t.second_troop)} ",
                        type=Types.Text.KMD),
                    Element.Button(
                        "选取",
                        value=json.dumps({'type': 'match_select_players',
                                          'kookId': t.kookId,
                                          'playerId': t.playerId,
                                          'match_id': '9'}),
                        click=Types.Click.RETURN_VAL,
                        theme=Types.Theme.INFO,
                    ),
                ))
                card8.append(Module.Divider())
            z_select = SelectPlayerMatchData()
            z_select.need_to_select = remove_team_manager_user_list
            MatchConditionEx.blmm_1 = z_select

            CommandChannel = await bot.client.fetch_public_channel(OldGuildChannel.command_channel)
            await CommandChannel.send(f'(met){first_team_o}(met) 第1队伍队长')
            await CommandChannel.send(f'(met){second_team_o}(met) 第2队伍队长')

            await msg.reply(CardMessage(card8))
        pass

    @bot.command(name='test_abc', case_sensitive=False)
    async def test_abc(msg: Message):
        with get_session() as sqlSession:
            name_x_initial = ServerManager.getServerName(ServerEnum.Server_1)
            result = (sqlSession.query(DB_WillMatchs).order_by(desc(DB_WillMatchs.time_match))
                      .filter(DB_WillMatchs.server_name == name_x_initial,
                              DB_WillMatchs.is_cancel == 0,
                              DB_WillMatchs.is_finished == 0,
                              )).limit(1).count()

            await  msg.reply(f'服务器：{name_x_initial} :{result},')

            use_server_x = ServerEnum.Server_2
            name_x_initial = ServerManager.getServerName(use_server_x)
            result = (sqlSession.query(DB_WillMatchs).order_by(desc(DB_WillMatchs.time_match))
                      .filter(DB_WillMatchs.server_name == name_x_initial,
                              DB_WillMatchs.is_cancel == 0,
                              DB_WillMatchs.is_finished == 0,
                              )).limit(1).count()

            await  msg.reply(f'服务器：{name_x_initial} :{result},')

    @bot.command(name='show_match', case_sensitive=False, aliases=['sm'])
    async def show_match(msg: Message):
        user_list = ['482714005', '1555061634', '1932416737', '3551233689', '3484257139', '180475151', '3394658957',
                     '2806603494', '1384765669', '1510300409', '569326827', '3784439652']
        # user_list = ['482714005', '1555061634']
        print('123')
        global sqlSession
        sqlSession = get_session()
        z = sqlSession.execute(select(DB_Player).where(DB_Player.kookId.in_(user_list))).scalars()
        # z = sqlSession.query(Player).filter(Player.kookId.in_(user_list)).all()
        dict_for_kook_id = {}
        for i in z:
            t: DB_Player = i
            dict_for_kook_id[t.kookId] = t

        player_list = []
        for id, user in enumerate(user_list):
            player: DB_Player = dict_for_kook_id[user]
            player_info = PlayerBasicInfo({'username': player.kookName})
            player_info.score = player.rank
            player_info.user_id = player.kookId
            player_info.username = player.kookName
            player_info.player_id = player.playerId
            # print(player_info.username)
            player_list.append(player_info)

        if len(player_list) < 12:
            await msg.reply(f'注册人数不足12，请大伙先注册，/help可以提供支持')
        if len(player_list) % 2 != 0:
            await msg.reply(f'人数非奇数！')
            return
        divide_data: DivideData = MatchState.divide_player_ex(player_list)

        will_match_data = DB_WillMatchs()
        will_match_data.time_match = datetime.datetime.now()
        will_match_data.match_id = str(uuid.uuid1())
        will_match_data.set_first_team_player_ids(divide_data.get_first_team_player_ids())
        will_match_data.set_second_team_player_ids(divide_data.get_second_team_player_ids())

        first_faction, second_faction = get_random_faction_2()
        will_match_data.first_team_culture = first_faction
        will_match_data.second_team_culture = second_faction

        will_match_data.match_type = WillMatchType.Match88
        will_match_data.is_cancel = False
        will_match_data.is_finished = False
        will_match_data.server_name = 'CN_BTL_NINGBO_1'
        will_match_data.match_id_2 = 100

        print(1213)
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:14725/send_match_info',
                                    json=will_match_data.to_dict()) as response:
                return await response.text()
        # 获取今天的日期并设置时间为 00:00:00
        today_midnight = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        result_temp = len(sqlSession.execute(
            select(DB_WillMatchs).where(DB_WillMatchs.time_match >= today_midnight)).all())
        newest_data = sqlSession.execute(
            select(DB_WillMatchs).where(DB_WillMatchs.time_match >= today_midnight).order_by(
                desc(DB_WillMatchs.time_match)).limit(1)).first()

        last_match_number = random.randint(3, 10)
        if newest_data is not None and len(newest_data) > 0:
            last_match_number += newest_data[0].match_id_2

        will_match_data.match_id_2 = last_match_number

        try:
            sqlSession.add(will_match_data)
        except Exception as e:
            print(e.with_traceback())
            sqlSession.rollback()
        else:
            sqlSession.commit()

        await msg.reply(CardMessage(
            Card(
                Module.Header('分队情况表'),
                Module.Divider(),
                Module.Header(f'时间:{get_time_str()}'),
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(divide_data.get_attacker_names(), type=Types.Text.KMD),
                        Element.Text(divide_data.get_attacker_scores(), type=Types.Text.KMD),
                        Element.Text('game_info', type=Types.Text.KMD),
                    )
                ),
                Module.Divider(),
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(divide_data.get_defender_names(), type=Types.Text.KMD),
                        Element.Text(divide_data.get_defender_scores(), type=Types.Text.KMD),
                        Element.Text('game_info', type=Types.Text.KMD),
                    )
                ),
                Module.Divider(),
                Module.Header(f'比赛ID：{will_match_data.match_id_2}')
            )
        ))
        pass

    @bot.command(name='show_match_2', case_sensitive=False, aliases=['sm2'])
    async def show_match(msg: Message):
        # user_list = ['482714005', '1757472132']
        user_list = ['482714005', '1386568452']  # 平克曼
        print('123')
        global sqlSession
        sqlSession = get_session()
        z = sqlSession.execute(select(DB_Player).where(DB_Player.kookId.in_(user_list))).scalars()
        # z = sqlSession.query(Player).filter(Player.kookId.in_(user_list)).all()
        dict_for_kook_id = {}
        for i in z:
            t: DB_Player = i
            dict_for_kook_id[t.kookId] = t

        player_list = []
        for id, user in enumerate(user_list):
            player: DB_Player = dict_for_kook_id[user]
            player_info = PlayerBasicInfo({'username': player.kookName})
            player_info.score = player.rank
            player_info.user_id = player.kookId
            player_info.username = player.kookName
            player_info.player_id = player.playerId
            # print(player_info.username)
            player_list.append(player_info)

        if len(player_list) % 2 != 0:
            await msg.reply(f'人数非奇数！')
            return
        divide_data: DivideData = MatchState.divide_player_ex(player_list)

        will_match_data = DB_WillMatchs()
        will_match_data.time_match = datetime.datetime.now()
        will_match_data.match_id = str(uuid.uuid1())
        will_match_data.set_first_team_player_ids(divide_data.get_first_team_player_ids())
        will_match_data.set_second_team_player_ids(divide_data.get_second_team_player_ids())

        first_faction, second_faction = get_random_faction_2()
        will_match_data.first_team_culture = first_faction
        will_match_data.second_team_culture = second_faction

        will_match_data.match_type = WillMatchType.Test11
        will_match_data.is_cancel = False
        will_match_data.is_finished = False
        will_match_data.server_name = 'CN_BTL_NINGBO_1'

        # 获取今天的日期并设置时间为 00:00:00
        today_midnight = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        result_temp = len(sqlSession.execute(
            select(DB_WillMatchs).where(DB_WillMatchs.time_match >= today_midnight)).all())
        newest_data = sqlSession.execute(
            select(DB_WillMatchs).where(DB_WillMatchs.time_match >= today_midnight).order_by(
                desc(DB_WillMatchs.time_match)).limit(1)).first()

        last_match_number = random.randint(3, 10)
        if newest_data is not None and len(newest_data) > 0:
            last_match_number += newest_data[0].match_id_2

        will_match_data.match_id_2 = last_match_number

        try:
            sqlSession.add(will_match_data)
        except Exception as e:
            print(e.with_traceback())
            sqlSession.rollback()
        else:
            sqlSession.commit()

        await msg.reply(CardMessage(
            Card(
                Module.Header('分队情况表'),
                Module.Divider(),
                Module.Header(f'时间:{get_time_str()}'),
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(divide_data.get_attacker_names(), type=Types.Text.KMD),
                        Element.Text(divide_data.get_attacker_scores(), type=Types.Text.KMD),
                        Element.Text('game_info', type=Types.Text.KMD),
                    )
                ),
                Module.Divider(),
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(divide_data.get_defender_names(), type=Types.Text.KMD),
                        Element.Text(divide_data.get_defender_scores(), type=Types.Text.KMD),
                        Element.Text('game_info', type=Types.Text.KMD),
                    )
                ),
                Module.Divider(),
                Module.Header(f'比赛ID：{will_match_data.match_id_2}')
            )
        ))
        pass

    @bot.command(name='reac', case_sensitive=False)
    async def worldO(msg: Message):
        # 公告区
        ch = await bot.client.fetch_public_channel(ChannelManager.announcement)
        print('123')
        # 使用channel对象的send
        # ret = await ch.send("这是一个测试信息,使用了ch.send")  # 方法1

        # 往其他频道发送信息
        # 使用bot对象的client.send
        # ret = await bot.client.send(ch, "这是一个测试信息，使用了bot.client.send")  # 方法2
        # print(f"bot.client.send | msg_id {ret['msg_id']}")  # 方法2 发送消息的id
        # await msg.reply('')

        # data = {'target_id': ChannelManager.match_set_channel, 'array': json.dumps(list_t)}
        # requests.post(UrlHelper.move_user, data)
        # await msg.reply('移动成功')
        # pass
        # guild = await bot.client.fetch_guild(ChannelManager.sever)
        # rolse = await guild.fetch_roles()
        # for i in rolse:
        #     print(i.name)
