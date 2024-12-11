from khl import Bot, Message, EventTypes, Event, GuildUser, PublicChannel
from khl.card import Card, Module, Element, Types, CardMessage, Struct
from sqlalchemy import literal, desc, text

from LogHelper import LogHelper
from blmm_bot import EsChannels, guard, move_a_to_b_ex
from init_db import get_session
from kook.ChannelKit import ChannelManager
from lib.basic import generate_numeric_code
from match_state import PlayerBasicInfo, MatchState, DivideData
from tables import *
from tables.Admin import DBAdmin
from tables.PlayerNames import DB_PlayerNames

session = get_session()
g_channels: EsChannels


def init(bot: Bot, es_channels: EsChannels):
    global g_channels
    g_channels = es_channels

    @bot.command(name='reset_state_machine', case_sensitive=False, aliases=['rsm'])
    async def reset_state_machine(mgs: Message):
        if mgs.author_id == ChannelManager.es_user_id:
            global stateMachine
            stateMachine = MatchState()
            await mgs.reply('已重置状态机' + str(stateMachine.__dict__))
        else:
            await mgs.reply('[Warning]:do not use es command!')
        pass

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