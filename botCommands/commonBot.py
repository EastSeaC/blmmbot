import json
from datetime import datetime

from khl import Bot, EventTypes, Event

from botCommands.ButtonValueImpl import AdminButtonValue
from lib.LogHelper import LogHelper
from init_db import get_session
from kook.ChannelKit import EsChannels, ChannelManager
from lib.SelectMatchData import SelectPlayerMatchData
from lib.ServerManager import ServerManager
from lib.match_state import MatchConditionEx
from tables import *
from tables.ResetPlayer import DB_ResetPlayer

session = get_session()
g_channels: EsChannels


def get_troop_type_name(a: int):
    if a == 1:
        return "步兵"
    elif a == 2:
        return "骑兵"
    elif a == 3:
        return "射手"
    else:
        return "未选择"


def init(bot: Bot, es_channels: EsChannels):
    global g_channels
    g_channels = es_channels

    @bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
    async def btn_click_event(b: Bot, e: Event):
        """按钮点击事件"""
        print(e.target_id)
        print(e.body, "\n")
        value = str(e.body['value'])
        user_id = e.body['user_id']
        guild_id = e.body['guild_id']

        if value.startswith('{'):
            btn_value_dict: dict = json.loads(value)
            if 'type' in btn_value_dict.keys():
                type = str(btn_value_dict.get('type', 'invalid'))
                selected_players = btn_value_dict.get('kookId')
                if type == 'match_select_players':
                    selectPlayerMatchData: SelectPlayerMatchData = MatchConditionEx.blmm_1
                    if user_id in '482714005':
                        selectPlayerMatchData.first_team_player_ids.append(selected_players)
                    elif user_id in '1555061634':
                        selectPlayerMatchData.second_team_player_ids.append(selected_players)
                    else:
                        print('你不是队长，禁止选取队员')
                    selectPlayerMatchData.need_to_select = selectPlayerMatchData.need_to_select.remove(selected_players)
        elif value == AdminButtonValue.Refresh_Server_Force:
            if user_id not in ChannelManager.manager_user_id:
                channel = await b.client.fetch_public_channel(ChannelManager.get_command_channel_id(guild_id))
                await channel.send(
                    f'(met){user_id}(met) 禁止使用管理员指令')
                return
        elif value == AdminButtonValue.Reset_Server_ChannelSet:
            channel = await b.client.fetch_public_channel(ChannelManager.get_command_channel_id(guild_id))
            if ChannelManager.is_admin(user_id):

                pass
            else:
                await channel.send(f'(met){user_id}(met) 禁止使用管理员指令')

        elif value == AdminButtonValue.Refresh_Server_Force or value == AdminButtonValue.Refresh_Server6_Force:
            print('test-1')
            channel = await b.client.fetch_public_channel(ChannelManager.get_command_channel_id(guild_id))
            if user_id not in ChannelManager.manager_user_id:
                await channel.send(f'(met){user_id}(met) 禁止使用管理员指令')
                return
            if value == AdminButtonValue.Refresh_Server_Force:
                ServerManager.RestartBLMMServer(5)
            else:
                ServerManager.RestartBLMMServer(6)
            await channel.send(f'(met){user_id}(met) 服务器重启成功')

        else:
            with get_session() as sql_session:
                t = sql_session.query(Player).filter(Player.kookId == user_id)
                channel = await b.client.fetch_public_channel(ChannelManager.get_command_channel_id(guild_id))

                if t.count() == 1:
                    player: Player = t.first()

                    is_first_troop = False
                    if value.startswith('f'):
                        troop_type = int(value[1])
                        player.first_troop = troop_type
                        is_first_troop = True
                    elif value.startswith('s'):
                        troop_type = int(value[1])
                        player.second_troop = troop_type
                    troop_name = get_troop_type_name(troop_type)

                    try:
                        sql_session.merge(player)
                        sql_session.commit()
                        await channel.send(
                            f'(met){user_id}(met) 你设置了你的第{1 if is_first_troop else 2}兵种为{troop_name}')
                    except Exception as e:
                        await channel.send(
                            f'(met){user_id}(met) 机器人异常，联系管理员')
                        sql_session.rollback()

                else:
                    await channel.send(
                        f'(met){user_id}(met) 你没有注册，请先注册')
