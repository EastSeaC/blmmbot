from datetime import datetime

from khl import Bot, Message, EventTypes, Event, GuildUser, PublicVoiceChannel
from sqlalchemy import select

from LogHelper import LogHelper, get_time_str
from init_db import get_session
from kook.ChannelKit import ChannelManager, EsChannels
from match_guard import MatchGuard
from match_state import PlayerBasicInfo, MatchState, DivideData, MatchCondition
from tables import *
from tables import DB_WillMatch
from tables.DB_WillMatch import DB_WillMatchs

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
        if msg.author_id not in ChannelManager.manager_user_id:
            await msg.reply('禁止使用管理员指令')

        if count >= 1:
            if str(args[0]).isdecimal():
                match_id_2 = int(args[0])

                sql_session = get_session()
                today_midnight = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
                z = sql_session.execute(select(DB_WillMatchs).where(DB_WillMatchs.time_match >= today_midnight,
                                                                    DB_WillMatchs.match_id_2 == match_id_2)).first()

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
        z = session.query(Player).filter(Player.kookId.in_([i.id for i in k])).all()
        dict_for_kook_id = {}
        for i in z:
            t: Player = i
            dict_for_kook_id[t.kookId] = t

        # print([i.__dict__ for i in z])
        # print([i.__dict__ for i in dict_for_kook_id.values()])
        try:
            for id, user in enumerate(k):
                t: GuildUser = user
                player: Player = dict_for_kook_id[t.id]
                player_info = PlayerBasicInfo({})
                player_info.score = player.rank
                player_info.user_id = t.id
                player_info.kook_name = t.username
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

    @bot.task.add_interval(seconds=1)
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
            channel = await bot.client.fetch_public_channel(ChannelManager.match_wait_channel)
            k = await channel.fetch_user_list()
            number = len(k)
            # stateMachine.player_number = number
            # for i in k:
            #     t: GuildUser = i
            #     print(t.id, t.joined_at)
            # stateMachine.add_player_to_wait_list(t.id)
            pass
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
