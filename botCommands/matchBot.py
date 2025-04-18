import json
import uuid
from datetime import datetime, timedelta

from khl import Bot, Message, EventTypes, Event, GuildUser, PublicVoiceChannel
from khl.card import CardMessage, Card, Module, Element, Types
from sqlalchemy import select, desc

from botCommands.playerBot import convert_timestamp
from entity.ServerEnum import ServerEnum
from lib.DividePlayerEx2 import balance_teams
from lib.LogHelper import LogHelper, get_time_str
from init_db import get_session
from kook.ChannelKit import ChannelManager, EsChannels, OldGuildChannel
from lib.SelectMatchData import SelectPlayerMatchData
from lib.ServerManager import ServerManager
from lib.match_guard import MatchGuard
from lib.match_state import PlayerBasicInfo, MatchState, DivideData, MatchCondition, MatchConditionEx
from tables import *
from tables.Ban import DB_Ban
from tables.WillMatch import DB_WillMatchs

session = get_session()
g_channels: EsChannels
stateMachine: MatchState = MatchState()


def init(bot: Bot, es_channels: EsChannels):
    global g_channels
    g_channels = es_channels
    guard = MatchGuard()

    async def move_a_to_b_ex(b: str, list_player: list):
        channel_b = await bot.client.fetch_public_channel(b)
        for id, user_id in enumerate(list_player):
            await channel_b.move_user(b, user_id)

    @bot.command(name='reset_state_machine', case_sensitive=False, aliases=['rsm'])
    async def reset_state_machine(mgs: Message):
        if mgs.author_id == ChannelManager.es_user_id:
            global stateMachine
            stateMachine = MatchState()
            await mgs.reply('已重置状态机' + str(stateMachine.__dict__))
        else:
            await mgs.reply('[Warning]:do not use es command!')
        pass

    @bot.command(name='show_player_numbers_in_waiting_channel', case_sensitive=False, aliases=['spniwc', 'spn'])
    async def show_player_numbers_in_waiting_channel(msg: Message):
        # 查看在等候频道里的玩家
        await msg.reply('当前等候频道里的玩家有:' + str(stateMachine.player_number))

    @bot.command(name='state', case_sensitive=False, aliases=['st'])
    async def state_command(msg: Message, action: str = ''):
        result_str = ''
        if msg.author_id == ChannelManager.es_user_id:
            if action == 'reset':
                global stateMachine
                stateMachine = MatchState()
                result_str = '初始化成功'
            elif action == 'sx':

                pass
            else:
                await msg.reply('[Warning]:字符串为空')
            pass
        else:
            await msg.reply('[Warning]:do not use es command!')

    @bot.command(name='cancel_match', case_sensitive=False, aliases=['cnm'])
    async def cancel_match(msg: Message, *args):
        count = len(args)
        if not ChannelManager.is_organization_user(msg.author_id):
            await msg.reply('禁止使用管理员指令')
            return

        if count >= 1:
            if str(args[0]).isdecimal():
                match_id_2 = int(args[0])

                sql_session = get_session()
                today_midnight = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
                z = sql_session.execute(select(DB_WillMatchs).where(DB_WillMatchs.match_id_2 == match_id_2)).first()

                # print(z)
                if z is None or len(z) == 0:
                    await msg.reply('比赛ID 错误')
                    return
                will_match: DB_WillMatchs = z[0]
                if will_match.is_cancel is True or will_match.is_finished is True:
                    await  msg.reply(f'比赛ID {will_match.match_id_2} 已结束或者取消， 不再接受操作')
                else:
                    will_match.is_cancel = True
                    will_match.cancel_reason = f'管理员{msg.author.username}于{get_time_str()}取消'
                    try:
                        sql_session.add(will_match)
                        sql_session.commit()
                        await msg.reply(f'比赛ID:{will_match.match_id_2}被' + will_match.cancel_reason)
                    except Exception as e:
                        await msg.reply(f'比赛ID:{will_match.match_id_2} 无法取消，服务器异常，请联系管理员')
                        sql_session.rollback()
        else:
            await msg.reply('指令异常')

    @bot.command(name='select_mode', case_sensitive=False)
    async def select_mode_play_match(msg: Message, arg: str = ''):
        """
        选人模式
        """
        if not ChannelManager.is_organization_user(msg.author_id):
            await msg.reply('禁止使用管理员指令')
            return
        print(msg.ctx.channel)
        if msg.ctx.channel != OldGuildChannel.command_select_channel:
            await msg.reply('禁止在非 选人指令频道 使用')
            return

        sqlSession = get_session()
        # use_server_x = ServerEnum.Server_1
        # if is_force_use_2:
        #     use_server_x = ServerEnum.Server_2
        # else:
        #     use_server_x = ServerEnum.Server_1
        # import datetime as dt_or
        name_x_initial = ServerManager.getServerName(ServerEnum.Server_1)
        LogHelper.log('name_x_initial: ' + name_x_initial)
        result = (sqlSession.query(DB_WillMatchs).order_by(desc(DB_WillMatchs.time_match))
                  .filter(DB_WillMatchs.server_name == name_x_initial,
                          DB_WillMatchs.is_cancel == 0,
                          DB_WillMatchs.is_finished == 0,
                          )).limit(1).count()

        if result == 0:
            use_server_x = ServerEnum.Server_1
            LogHelper.log(f'first_result {use_server_x} {result}')
            pass
        elif result > 0:
            use_server_x = ServerEnum.Server_2
            name_x_initial = ServerManager.getServerName(use_server_x)
            result = (sqlSession.query(DB_WillMatchs).order_by(desc(DB_WillMatchs.time_match))
                      .filter(DB_WillMatchs.server_name == name_x_initial,
                              DB_WillMatchs.is_cancel == 0,
                              DB_WillMatchs.is_finished == 0,
                              )).limit(1).count()
            if result == 0:
                use_server_x = ServerEnum.Server_2
                LogHelper.log(f'server result: {use_server_x} {result}')
            if result > 0:
                name_x_initial = ServerManager.getServerName(ServerEnum.Server_3)
                result = (sqlSession.query(DB_WillMatchs).order_by(desc(DB_WillMatchs.time_match))
                          .filter(DB_WillMatchs.server_name == name_x_initial,
                                  DB_WillMatchs.is_cancel == 0,
                                  DB_WillMatchs.is_finished == 0,
                                  )).limit(1).count()
                if result == 0:
                    use_server_x = ServerEnum.Server_3
                    LogHelper.log(f'server result: {use_server_x} {result}')
                else:
                    await msg.reply('暂无服务器，请稍等')
                    return

        command_select_channel_obj = await  bot.client.fetch_public_channel(OldGuildChannel.command_select_channel)
        channel = await bot.client.fetch_public_channel(OldGuildChannel.match_select_channel)
        voice_channel: PublicVoiceChannel = channel

        k = await voice_channel.fetch_user_list()
        for i in k:
            z: GuildUser = i
            # print(z.__dict__)
            # print(convert_timestamp(z.active_time))

        number_of_user = len(k)
        if number_of_user % 2 == 1 or number_of_user == 0:
            await msg.reply(f'人数异常, 当前人数为 {len(k)} , 必须为非0偶数')
            return

        player_list = []
        player_list_ax = []

        sqlSession = get_session()
        z = sqlSession.query(DB_Player).filter(DB_Player.kookId.in_([i.id for i in k])).all()
        dict_for_kook_id = {}
        for i in z:
            t: DB_Player = i
            dict_for_kook_id[t.kookId] = t

        try:
            ban_player_kook_id = sqlSession.execute(
                select(DB_Ban.kookId).where(DB_Ban.endAt >= datetime.now())).scalars().all()
            for i in ban_player_kook_id:
                if i in dict_for_kook_id:
                    player_x_ban: DB_Player = dict_for_kook_id[i]
                    await msg.reply(f'有被封印玩家 {player_x_ban.kookName} (met){player_x_ban.kookId}(met) 停止匹配')
                    return
        except Exception as e:
            print(e)

        try:
            for id, user in enumerate(k):
                t: GuildUser = user
                if t.id not in dict_for_kook_id:
                    await command_select_channel_obj.send(f'(met){t.id}(met) 你没有注册，请先注册')
                    await move_a_to_b_ex(OldGuildChannel.match_set_channel, [t.id])  # 移动到普通频道
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

                player_list_ax.append(
                    (player.kookId, player.infantry_score, player.cavalry_score, player.archer_score))

        except Exception as e:
            print(repr(e))
            LogHelper.log(f"没有注册 {t.id} {t.username}")
            await command_select_channel_obj.send(f'(met){t.id}(met) 你没有注册，请先注册 Exception!')
            await move_a_to_b_ex(ChannelManager.match_set_channel, [t.id])
            return

        # 降序排列（从大到小）
        sorted_player_list = sorted(player_list, key=lambda x: x.score, reverse=True)
        first_team_o = sorted_player_list[0].user_id
        print(sorted_player_list[0].score)
        second_team_o = sorted_player_list[1].user_id
        print(sorted_player_list[1].score)
        #
        SelectPlayerMatchData.start_run()
        SelectPlayerMatchData.first_team_master = first_team_o
        SelectPlayerMatchData.second_team_master = second_team_o
        SelectPlayerMatchData.need_to_select = [i.user_id for i in player_list]
        SelectPlayerMatchData.origin_list = SelectPlayerMatchData.need_to_select
        MatchConditionEx.blmm_2 = SelectPlayerMatchData.need_to_select
        print(SelectPlayerMatchData.need_to_select)
        SelectPlayerMatchData.cur_index = 0
        SelectPlayerMatchData.first_team_player_ids = [first_team_o]
        SelectPlayerMatchData.second_team_player_ids = [second_team_o]
        SelectPlayerMatchData.total_list = [first_team_o, second_team_o]
        SelectPlayerMatchData.data = dict_for_kook_id

        card8 = Card()
        for i, t in dict_for_kook_id.items():
            if i in SelectPlayerMatchData.need_to_select:
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

        await command_select_channel_obj.send(f'(met){first_team_o}(met) 第1队伍队长')
        await command_select_channel_obj.send(f'(met){second_team_o}(met) 第2队伍队长')
        await msg.reply(CardMessage(card8))
        await command_select_channel_obj.send(
            f'{ChannelManager.get_at(SelectPlayerMatchData.get_cur_select_master_ex())} 你该选人了（10s)')
        await command_select_channel_obj.send(CardMessage(Card(
            Module.Countdown(
                datetime.now() + timedelta(seconds=12), mode=Types.CountdownMode.SECOND
            )
        )))

        need_to_select_list = []
        card8 = Card(
            Module.Section(f'队长1：{ChannelManager.get_at(first_team_o)}，队长2：{ChannelManager.get_at(second_team_o)}'),
            Module.Divider(),
        )
        for i, v in dict_for_kook_id.items():
            t: DB_Player = v
            print(f"{t.kookName},{t.rank} ")
            if t.kookId == first_team_o or t.kookId == second_team_o:
                continue

            need_to_select_list.append(t.kookId)
            # SelectPlayerMatchData.need_to_select.append(t.kookId)
            print(need_to_select_list)
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
        # 考虑？
        SelectPlayerMatchData.need_to_select = need_to_select_list
        await command_select_channel_obj.send(CardMessage(card8))
        # await msg.reply(CardMessage(card8))
        # will_match_data = DB_WillMatchs()
        # will_match_data.time_match = datetime.now()
        # will_match_data.match_id = str(uuid.uuid1())
        # will_match_data.set_first_team_player_ids(divide_data.get_first_team_player_ids())
        # # will_match_data.set_second_team_player_ids(divide_data.get_second_team_player_ids())
        #
        # first_faction, second_faction = get_random_faction_2()
        # will_match_data.first_team_culture = first_faction
        # will_match_data.second_team_culture = second_faction
        #
        # will_match_data.match_type = WillMatchType.Match88
        # will_match_data.is_cancel = False
        # will_match_data.is_finished = False
        # will_match_data.server_name = 'CN_BTL_NINGBO_1'
        # cm = CardMessage(Card(
        #
        # ))
        return

    @bot.command(name='ae', case_sensitive=False, aliases=['a'])
    async def american_style_divide(msg: Message, arg: str):
        if not ChannelManager.is_organization_user(msg.author_id):
            await msg.reply('禁止使用管理员指令')
            return

        is_no_move = False
        is_exclude_es = False
        is_force_use_2 = False
        is_force_use_3 = False
        not_open_server = False
        for i in arg:
            if i == 'e':
                is_exclude_es = True
            elif i == 'n':
                is_no_move = True
            elif i == 'x' or i == '2':
                is_force_use_2 = True
            elif i == 'z':
                not_open_server = True
            elif i == '1':
                is_force_use_2 = False
                is_force_use_3 = False
            elif i == 't':
                is_force_use_2 = False
                is_force_use_3 = True
            elif i == '3':
                is_force_use_2 = False
                is_force_use_3 = True

        channel = await bot.client.fetch_public_channel(
            ChannelManager.match_high_score_match_channel)
        voice_channel: PublicVoiceChannel = channel

        k = await es_channels.wait_channel.fetch_user_list()
        for i in k:
            z: GuildUser = i
            print(z.__dict__)
            print(convert_timestamp(z.active_time))
            if is_exclude_es:
                if z.id == ChannelManager.es_user_id:
                    k.remove(z)

        number_of_user = len(k)
        if number_of_user % 2 == 1 or number_of_user == 0:
            await msg.reply(f'人数异常, 当前人数为 {len(k)} , 必须为非0偶数')
            return
        player_list = []
        player_list_ax = []

        sqlSession = get_session()
        z = sqlSession.query(DB_Player).filter(DB_Player.kookId.in_([i.id for i in k])).all()
        dict_for_kook_id = {}
        for i in z:
            t: DB_Player = i
            dict_for_kook_id[t.kookId] = t

        try:
            ban_player_kook_id = sqlSession.execute(select(DB_Ban.kookId).where(DB_Ban.endAt >= datetime.now())).all()
            for i in ban_player_kook_id:
                if i in dict_for_kook_id:
                    player_x_ban: DB_Player = dict_for_kook_id[i]
                    await msg.reply(f'有被封印玩家 {player_x_ban.kookName} (met){player_x_ban.kookId}(met) 停止匹配')
                    return
        except Exception as e:
            print(e)

        try:
            for id, user in enumerate(k):
                t: GuildUser = user
                if t.id not in dict_for_kook_id:
                    await es_channels.command_channel.send(f'(met){t.id}(met) 你没有注册，请先注册')
                    await move_a_to_b_ex(OldGuildChannel.match_set_channel, [t.id])  # 移动到普通频道
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

                player_list_ax.append(
                    (player.kookId, player.infantry_score, player.cavalry_score, player.archer_score))

        except Exception as e:
            print(repr(e))
            LogHelper.log(f"没有注册 {t.id} {t.username}")
            await es_channels.command_channel.send(f'(met){t.id}(met) 你没有注册，请先注册 Exception!')
            await move_a_to_b_ex(ChannelManager.match_set_channel, [t.id])
            return

        team_a, team_b, score_diff = balance_teams(player_list_ax)

    @bot.command(name='rtc', case_sensitive=False, aliases=['yc'])
    async def tojadx(msg: Message):
        if ChannelManager.is_common_user(msg.author_id):
            await msg.reply('禁止使用es指令')
            return

        k = await es_channels.wait_channel.fetch_user_list()

        if len(k) % 2 == 1:
            await msg.reply('人数异常')
            return
        player_list = []

        session.commit()
        z = session.query(DB_Player).filter(DB_Player.kookId.in_([i.id for i in k])).all()
        dict_for_kook_id = {}
        for i in z:
            t: DB_Player = i
            dict_for_kook_id[t.kookId] = t

        # print([i.__dict__ for i in z])
        # print([i.__dict__ for i in dict_for_kook_id.values()])
        try:
            for id, user in enumerate(k):
                t: GuildUser = user
                player: DB_Player = dict_for_kook_id[t.id]
                player_info = PlayerBasicInfo({})
                player_info.score = player.rank
                player_info.user_id = t.id
                player_info.kook_name = t.username

                player_info.first_troop = player.first_troop
                player_info.second_troop = player.second_troop

                player_list.append(player_info)
        except Exception as e:
            LogHelper.log(f"没有注册 {t.id} {t.username}")
            await es_channels.command_channel.send(f'(met){t.id}(met) 你没有注册，请先注册')
            await move_a_to_b_ex(ChannelManager.match_wait_channel, [t.id])
            return
            # if len(player_list) % 2 != 0:
        #     player_list.pop()

        divide_data: DivideData = MatchState.divide_player_ex(player_list)
        print(divide_data.attacker_list)
        print(divide_data.defender_list)
        await move_a_to_b_ex(ChannelManager.match_attack_channel, divide_data.attacker_list)
        await move_a_to_b_ex(ChannelManager.match_defend_channel, divide_data.defender_list)

        await msg.reply('分配完毕!')

    @bot.on_event(EventTypes.JOINED_CHANNEL)
    async def player_join_channel(b: Bot, e: Event):
        # 事件，玩家加入频道
        channel_id = e.body["channel_id"]
        user_id = e.body["user_id"]
        guild = await bot.client.fetch_guild(ChannelManager.sever)
        user = await guild.fetch_user(user_id)

        if channel_id == ChannelManager.match_wait_channel:
            stateMachine.add_player_to_wait_list(user_id)
            z = f"{user.username}加入候选室成功, 当前人数{stateMachine.get_cur_player_num_in_wait_list()}"
            LogHelper.log(z)

            pass
        elif channel_id == ChannelManager.match_high_score_match_channel:
            with get_session() as session:
                p = session.query(DB_Player).filter(DB_Player.kookId == user_id).first()
                remove = False
                if p is None:
                    remove = True
                else:
                    player: DB_Player = p
                    if player.rank <= 1100:
                        remove = True

                # 移除
                if remove:
                    await move_a_to_b_ex(ChannelManager.match_wait_channel, [user_id])
        pass

    @bot.on_event(EventTypes.EXITED_CHANNEL)
    async def player_exit_channel(b: Bot, e: Event):
        channel_id = e.body["channel_id"]
        user_id = e.body["user_id"]

        if channel_id == ChannelManager.match_wait_channel:
            stateMachine.remove_player_from_wait_list(user_id=user_id)
            await es_channels.command_channel.send(f'1名玩家 离开等候频道，还剩下{stateMachine.get_match_num}')
            pass
        elif (channel_id == ChannelManager.match_attack_channel) or (channel_id == ChannelManager.match_defend_channel):
            warning_state, times = guard.add_warning_times(user_id)
            if warning_state:
                pass
            warning_text = f'(met){user_id}(met): 请注意,你已离开比赛频道{times}次'
            # 获取指定频道
            ch = await bot.client.fetch_public_channel(ChannelManager.announcement)
            ret = await ch.send(warning_text)  # 方法1
            # LogHelper.log(f" {ret['msg_id']}")  # 方法1 发送消息的id
            pass

    # @bot.task.add_interval(seconds=1)
    async def task_for_match():
        # 定时器
        global stateMachine
        condition = stateMachine.check_state()
        if condition == MatchCondition.DividePlayer:
            pass
            # await bot.client.move_user(
            #     target_id=ChannelManager.match_attack_channel, user_ids=stateMachine.attack_list)
            # await bot.client.move_user(
            #     target_id=ChannelManager.match_defend_channel, user_ids=stateMachine.defend_list)
        elif condition == MatchCondition.WaitingJoin:

            # channel = await bot.client.fetch_public_channel(ChannelManager.match_wait_channel)
            # k = await channel.fetch_user_list()
            # number = len(k)
            # stateMachine.player_number = number
            # for i in k:
            #     t: GuildUser = i
            #     print(t.id, t.joined_at)
            # stateMachine.add_player_to_wait_list(t.id)
            pass
        pass

    @bot.task.add_interval(minutes=5)
    async def cancel_outdated_match():
        with get_session() as session:
            outdated_matches = session.query(DB_WillMatchs).where(
                DB_WillMatchs.time_match < datetime.now() - timedelta(hours=1),
                DB_WillMatchs.is_cancel == 0,
                DB_WillMatchs.is_finished == 0,
            ).all()
            for i in outdated_matches:
                i.is_cancel = True
                i.cancel_reason = f'机器人于 {get_time_str()} 取消，超时'
                session.merge(i)

            session.commit()
        pass

    @bot.task.add_interval(seconds=3)
    async def task5():
        condition = stateMachine.check_state()
        if condition == MatchCondition.WaitingJoin:
            z: PublicVoiceChannel = es_channels.wait_channel
            user_list = await z.fetch_user_list()
            user_count = len(user_list)
            if user_count >= 12:
                pass
            # channel = await bot.client.fetch_public_channel(ChannelManager.command_channel)
            z = "当前状态为 等待玩家加入"
            # LogHelper.log(z)
            # await  es_channels.command_channel.send(z)
        elif condition == MatchCondition.DividePlayer:
            z = "当前状态为 划分玩家状态"
            # LogHelper.log(z)

            # await es_channels.command_channel.send(z)
        pass
