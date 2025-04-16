import json
from datetime import datetime
import datetime as dt_or

from khl import Bot, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types
from sqlalchemy import desc, select

from botCommands.ButtonValueImpl import AdminButtonValue, ESActionType, PlayerButtonValue
from entity.ServerEnum import ServerEnum
from kook.CardHelper import get_player_score_card, get_score_list_card
from lib.LogHelper import LogHelper, get_time_str
from init_db import get_session
from kook.ChannelKit import EsChannels, ChannelManager
from lib.SelectMatchData import SelectPlayerMatchData
from lib.ServerManager import ServerManager
from lib.match_state import MatchConditionEx
from tables import *
from tables import DB_WillMatch
from tables.DB_WillMatch import DB_WillMatchs
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
        channel_id = e.body['target_id']
        e_body_user_info = e.body['user_info']['username']

        # 这个代码虽然可以让所有人自由使用机器人，但是这会导致
        # 鸡婆拉屎，到处都是
        # channel = await b.client.fetch_public_channel(channel_id)
        channel = await b.client.fetch_public_channel(ChannelManager.get_command_channel_id(guild_id))
        if AdminButtonValue.is_admin_command(value):
            if not ChannelManager.is_admin(user_id):
                await channel.send(f'(met){user_id}(met) 禁止使用管理员指令')
                return
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
                elif type == ESActionType.Admin_Cancel_Match:
                    if not ChannelManager.is_admin(user_id):
                        await channel.send(f'(met){user_id}(met) 禁止使用管理员指令')
                        return
                    x = cancel_match(e_body_user_info, btn_value_dict['match_id_2'])
                    await channel.send(x)
                    pass

        elif value == AdminButtonValue.Restart_Server_1:  # 重启服务器
            if not ChannelManager.is_admin(user_id):
                await channel.send(f'(met){user_id}(met) 禁止使用管理员指令')
                return
            ServerManager.RestartBLMMServerEx(ServerEnum.Server_1)
        elif value == AdminButtonValue.Restart_Server_2:  # 重启服务器2
            if not ChannelManager.is_admin(user_id):
                await channel.send(f'(met){user_id}(met) 禁止使用管理员指令')
                return
            ServerManager.RestartBLMMServerEx(ServerEnum.Server_2)
        elif value == AdminButtonValue.Restart_Server_3:  # 重启服务器3
            if not ChannelManager.is_admin(user_id):
                await channel.send(f'(met){user_id}(met) 禁止使用管理员指令')
                return
            ServerManager.RestartBLMMServerEx(ServerEnum.Server_3)
            await channel.send(f'(met){user_id}(met) 服务器Server_3 已重启')
        elif value == AdminButtonValue.Show_Admin_Command:
            pass

        elif value == PlayerButtonValue.player_score:  # 玩家个人积分和 勋章
            channel = await b.client.fetch_public_channel(ChannelManager.get_command_channel_id(guild_id))

            cx = await get_player_score_card(user_id)
            await channel.send(cx)
        elif value == PlayerButtonValue.player_score_list:  # 积分列表
            channel = await b.client.fetch_public_channel(ChannelManager.get_command_channel_id(guild_id))
            cx = await get_score_list_card()
            await channel.send(cx)
        elif value == AdminButtonValue.Show_OrganizationPlayers:  # 查看组织管理
            channel = await b.client.fetch_public_channel(channel_id)
            await channel.send(
                f'(met){user_id}(met) ' + ' '.join(ChannelManager.organization_user_ids))
            return
        elif value == AdminButtonValue.Refresh_Server_Force:
            if user_id not in ChannelManager.manager_user_id:
                channel = await b.client.fetch_public_channel(ChannelManager.get_command_channel_id(guild_id))
                await channel.send(
                    f'(met){user_id}(met) 禁止使用管理员指令')
                return
        elif value == AdminButtonValue.Show_Server_State:  # 查看服务器 的比赛状态，需要发送一个新的卡片消息
            channel = await b.client.fetch_public_channel(ChannelManager.get_command_channel_id(guild_id))
            if not ChannelManager.is_admin(user_id):
                await channel.send(f'(met){user_id}(met) 禁止使用管理员指令')
                return
            c9 = show_server_state()
            cm = CardMessage(c9)
            await channel.send(cm)
            # await channel.send(f'(met){user_id}(met) 该指令{value}还未实现')
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
                ServerManager.RestartBLMMServerEx(server_index=ServerEnum.Server_1)
                ServerManager.RestartBLMMServerEx(ServerEnum.Server_2)
                ServerManager.RestartBLMMServerEx(ServerEnum.Server_3)
                # ServerManager.RestartBLMMServer(5)
            else:
                pass
                # ServerManager.RestartBLMMServer(6)
            await channel.send(f'(met){user_id}(met) 服务器重启成功')

        else:
            with get_session() as sql_session:
                t = sql_session.query(DB_Player).filter(DB_Player.kookId == user_id)
                channel = await b.client.fetch_public_channel(ChannelManager.get_command_channel_id(guild_id))

                if t.count() == 1:
                    player: DB_Player = t.first()

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


def show_server_state():
    with get_session() as sqlSession:
        server_names = [f'CN_BTL_NINGBO_{i}' for i in range(5, 6 + 1)]
        card = Card(
            Module.Header('服务器状态:' + get_time_str()),
        )

        result = (sqlSession.query(DB_WillMatchs).order_by(desc(DB_WillMatchs.time_match))
                  .filter(DB_WillMatchs.is_cancel == 0,
                          DB_WillMatchs.is_finished == 0)).all()

        for i in result:
            will_match: DB_WillMatchs = i
            card.append(Module.Section(
                Element.Text(
                    f'{will_match.server_name}: {will_match.get_match_description()} 比赛ID:{will_match.match_id_2}'),
                Element.Button(text='取消比赛',
                               value=json.dumps({'type': 'admin-cancel-match',
                                                 'match_id_2': will_match.match_id_2,
                                                 'server_name': will_match.server_name}),
                               theme=Types.Theme.DANGER)
            ))
            card.append(Module.Divider())
    return card


pass


def cancel_match(author_name: str, match_id_2: int):
    sql_session = get_session()
    today_midnight = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    z = sql_session.execute(select(DB_WillMatchs).where(DB_WillMatchs.time_match >= today_midnight,
                                                        DB_WillMatchs.match_id_2 == match_id_2)).first()

    # print(z)
    if z is None or len(z) == 0:
        return '比赛ID 错误'
    will_match: DB_WillMatchs = z[0]
    if will_match.is_cancel == 1 or will_match.is_finished == 1:
        return f'比赛ID {will_match.match_id_2} 已结束或者取消， 不再接受操作'
    else:
        will_match.is_cancel = 1
        will_match.cancel_reason = f'管理员{author_name}于{get_time_str()}取消'
        try:
            sql_session.merge(will_match)
            sql_session.commit()
            return f'比赛ID:{will_match.match_id_2}被' + will_match.cancel_reason
        except Exception as e:
            print(e)
            print(e.with_traceback())
            sql_session.rollback()
            return f'比赛ID:{will_match.match_id_2} 无法取消，服务器异常，请联系管理员'
