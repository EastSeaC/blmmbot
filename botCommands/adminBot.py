import json

from khl import Bot, Message, EventTypes, Event
from khl.card import Card, Module, Element, Types, CardMessage, Struct
from sqlalchemy import literal, desc

from blmm_bot import EsChannels
from init_db import get_session
from tables.Admin import DBAdmin
from tables import *
from tables.PlayerNames import DB_PlayerNames

session = get_session()
g_channels: EsChannels


class AdminButtonValue:
    Show_Last_Match = 'show_last_match'
    Show_Last_5_Matches = 'show_last_5_matches'
    Refresh_All_VerifyCode = 'Refresh_All_VerifyCode'


# 用于注册命令的函数
def init(bot: Bot, es_channels: EsChannels):
    global g_channels
    g_channels = es_channels

    # 必须写明命令的name
    @bot.command(name='es_adv', aliases=['es'])
    async def es_adv(msg: Message):
        cm = CardMessage()
        c8 = Card(
            Module.ActionGroup(
                Element.Button("显示最近5比赛", value=AdminButtonValue.Show_Last_5_Matches,
                               click=Types.Click.RETURN_VAL,
                               theme=Types.Theme.INFO),
                Element.Button("显示最近比赛", value=AdminButtonValue.Show_Last_Match, click=Types.Click.RETURN_VAL,
                               theme=Types.Theme.DANGER),
                Element.Button("刷新所有验证码", value=AdminButtonValue.Refresh_All_VerifyCode,
                               click=Types.Click.RETURN_VAL,
                               theme=Types.Theme.INFO)
            )
        )
        cm.append(c8)
        await es_channels.command_channel.send(cm)

    @bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
    async def btn_click_event(b: Bot, e: Event):
        """按钮点击事件"""
        print(e.target_id)
        print('*' * 45)
        print(e.body, "\n")

        kook_id = e.body['user_id']
        value = e.body['value']

        q = session.query(DBAdmin).filter(DBAdmin.kookId == kook_id)
        z = session.query(literal(True)).filter(q.exists()).scalar()
        print(z)
        if not z:
            await es_channels.command_channel.send("你不是管理员")
            return

        if value == AdminButtonValue.Refresh_All_VerifyCode:
            await RefreshAllPlayerVerifyCode()
        elif value == AdminButtonValue.Show_Last_Match:
            await ShowLastMatch()


async def RefreshAllPlayerVerifyCode():
    t = session.query(DB_PlayerNames).all()
    for i in t:
        player_names_obj: DB_PlayerNames = i
        very = Verify()
        very.playerId = i

        session.add()
    pass


async def ShowLastMatch():
    last_match = session.query(DB_Matchs).order_by(desc(DB_Matchs.time_match)).first()
    print('last_match', last_match)

    if last_match is not None:
        print(last_match.raw)
        c1 = Card(
            Module.Header(f"比赛时间为{last_match.time_match}\n服务器:{last_match.server_name}"),
            Module.Divider(),
        )
        await g_channels.command_channel.send(CardMessage(c1))
        match_raw = last_match.raw
        for i in last_match.raw.keys():
            player_match_data = last_match.raw[i]
            player_id = player_match_data['player_id']
            player_name = player_match_data['player_name']

            player_names_obj = session.query(DB_PlayerNames).filter(
                DB_PlayerNames.playerId == player_id).first()
            if player_names_obj is not None:
                t: DB_PlayerNames = player_names_obj
                player_name = t.PlayerName

            c2 = Card(
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(str(i), type=Types.Text.KMD),
                        Element.Text(f"名称:\n{player_name}", type=Types.Text.KMD),
                        Element.Text(f'KD比:\n{player_match_data["KillNum1"]}/{player_match_data["death"]}',
                                     type=Types.Text.KMD),
                    )
                )
            )
            await g_channels.command_channel.send(CardMessage(c2))
