import json
import random
import uuid
from datetime import datetime
import datetime as dt_or

from khl import Bot, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types
from sqlalchemy import desc, select

from botCommands.ButtonValueImpl import AdminButtonValue, ESActionType, PlayerButtonValue
from entity.ServerEnum import ServerEnum
from entity.WillMatchType import WillMatchType
from kook.CardHelper import get_player_score_card, get_score_list_card
from lib.LogHelper import LogHelper, get_time_str
from init_db import get_session
from kook.ChannelKit import EsChannels, ChannelManager, OldGuildChannel
from lib.SelectMatchData import SelectPlayerMatchData
from lib.ServerGameConfig import get_random_faction_2
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

    @bot.task.add_interval(seconds=1)
    async def task_for_select_match():
        if SelectPlayerMatchData.is_running:
            SelectPlayerMatchData.cur_waiting += 1
            print('cur', SelectPlayerMatchData.cur_waiting)
            if SelectPlayerMatchData.cur_waiting >= SelectPlayerMatchData.max_waiting:
                SelectPlayerMatchData.cur_waiting = 0
                channel = await bot.client.fetch_public_channel(OldGuildChannel.command_channel)

                x = random.sample(SelectPlayerMatchData.need_to_select, k=1)[0]
                print('x', x)
                if SelectPlayerMatchData.get_cur_select_master() == '1':
                    SelectPlayerMatchData.add_attacker(x)
                    await channel.send(ChannelManager.get_at(
                        SelectPlayerMatchData.get_cur_select_master_ex()) + f'你选取了{ChannelManager.get_at(x)}【系统随机】')
                elif SelectPlayerMatchData.get_cur_select_master() == '2':
                    SelectPlayerMatchData.add_defender(x)
                    await channel.send(ChannelManager.get_at(
                        SelectPlayerMatchData.get_cur_select_master_ex()) + f'你选取了{ChannelManager.get_at(x)}【系统随机】')

                card8 = Card()

                for i, t in SelectPlayerMatchData.data.items():
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

                if SelectPlayerMatchData.get_cur_select_master_ex() == -1:
                    print('test---------------------')
                    await channel.send(
                        f'{ChannelManager.get_at(SelectPlayerMatchData.first_team_master)} {ChannelManager.get_at(SelectPlayerMatchData.second_team_master)} 选人结束，请进入比赛服务器')

                    return
                else:
                    await channel.send(CardMessage(card8))
                    await channel.send(
                        ChannelManager.get_at(SelectPlayerMatchData.get_cur_select_master_ex()) + ':该你选人了')
                    await channel.send(CardMessage(Card(
                        Module.Countdown(
                            datetime.now() + dt_or.timedelta(seconds=12), mode=Types.CountdownMode.SECOND
                        )
                    )))

    @bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
    async def btn_click_event(b: Bot, e: Event):
        """按钮点击事件"""
        # print(e.target_id)
        # print(e.body, "\n")
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
                target_player_id = btn_value_dict.get('playerId')
                if type == 'match_select_players':
                    # selectPlayerMatchData: SelectPlayerMatchData = MatchConditionEx.blmm_1
                    # if user_id in '482714005':
                    # selectPlayerMatchData.first_team_player_ids.append(selected_players)
                    # elif user_id in '1555061634':
                    #     selectPlayerMatchData.second_team_player_ids.append(selected_players)
                    print('first_team_master', SelectPlayerMatchData.first_team_master)
                    print('second_team_master', SelectPlayerMatchData.second_team_master)
                    if user_id == SelectPlayerMatchData.first_team_master:
                        if SelectPlayerMatchData.get_cur_select_master() == '1':
                            await channel.send(ChannelManager.get_at(
                                SelectPlayerMatchData.first_team_master) + f'你选取了{ChannelManager.get_at(selected_players)}')
                            SelectPlayerMatchData.add_attacker(selected_players)
                        else:
                            await channel.send(ChannelManager.get_at(user_id) + ':不是你的回合，禁止选人')
                            return
                    elif user_id == SelectPlayerMatchData.second_team_master:
                        if SelectPlayerMatchData.get_cur_select_master() == '2':
                            SelectPlayerMatchData.add_defender(selected_players)
                            await channel.send(ChannelManager.get_at(
                                SelectPlayerMatchData.second_team_master) + f'你选取了{ChannelManager.get_at(selected_players)}')
                        else:
                            await channel.send(ChannelManager.get_at(user_id) + ':不是你的回合，禁止选人')
                            return
                    else:
                        await channel.send(f'{ChannelManager.get_at(user_id)} 你不是队长，禁止选取队员')
                        return

                    print('need_to_select变化前', SelectPlayerMatchData.need_to_select)
                    print(MatchConditionEx.blmm_2)
                    print('目标', selected_players)
                    # SelectPlayerMatchData.need_to_select = SelectPlayerMatchData.need_to_select.remove(selected_players)
                    print('变化后', SelectPlayerMatchData.need_to_select)

                    card8 = Card()

                    for i, t in SelectPlayerMatchData.data.items():
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
                    card8.append(Module.Divider())
                    await channel.send(CardMessage(card8))
                    await channel.send(
                        ChannelManager.get_at(SelectPlayerMatchData.get_cur_select_master_ex()) + ':该你选人了')

                    if len(SelectPlayerMatchData.need_to_select) == 0:
                        SelectPlayerMatchData.is_running = False
                        print('选人完毕')
                        will_match_data = DB_WillMatchs()
                        will_match_data.time_match = datetime.now()
                        will_match_data.match_id = str(uuid.uuid1())
                        will_match_data.set_first_team_player_ids(SelectPlayerMatchData.first_team_player_ids)
                        will_match_data.set_second_team_player_ids(SelectPlayerMatchData.second_team_player_ids)

                        first_faction, second_faction = get_random_faction_2()
                        will_match_data.first_team_culture = first_faction
                        will_match_data.second_team_culture = second_faction

                        will_match_data.match_type = WillMatchType.get_match_type_with_player_num(
                            len(SelectPlayerMatchData.first_team_player_ids))
                        will_match_data.is_cancel = False
                        will_match_data.is_finished = False

                        with get_session() as session:
                            session.add(will_match_data)
                            session.commit()



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

        # 玩家指令
        elif value == PlayerButtonValue.player_start_select_mode_match:
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
