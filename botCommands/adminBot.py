from khl import Bot, Message, EventTypes, Event, GuildUser, PublicChannel
from khl.card import Card, Module, Element, Types, CardMessage, Struct
from sqlalchemy import literal, desc, text

from lib.LogHelper import LogHelper
from blmm_bot import EsChannels
from init_db import get_session
from kook.ChannelKit import ChannelManager
from lib.basic import generate_numeric_code
from tables import *
from tables.Admin import DBAdmin
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

    # 初始化指令
    @bot.command(name='initial', aliases=['ini'])
    async def es_initial(msg: Message):
        try:
            await bot.client.fetch_public_channel(ChannelManager.command_channel)
            await  bot.client.delete_channel(ChannelManager.command_channel)
        except Exception as e:
            LogHelper.log(e.with_traceback())
        finally:
            guild = await bot.client.fetch_guild(ChannelManager.sever)
            await bot.client.create_text_channel(guild, '指令频道')

        pass

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

    @bot.command(name='es2', case_sensitive=False)
    async def es2(msg: Message):
        t = '''    /reset_state_machine
    
    /request_admin [playerId/userId] 申请成为管理
    /change_admin_level [playerId] [level] 修改管理员等级
    /cancel_admin [playerId/userId] 取消管理员
    
    /ban [gi/gu/ki/ku] [condition] 封印玩家
        说明：
        1.gi 类型为游戏PlayerID  举例 /ban gi 2.0.0.762.....
        2.gu 类型为游戏名称       例如 /ban gi doinb
        3.ki kook的userID        例如 /ban ki 222
        4.ku kook的用户名        例如  /ban ku 2123
    
    /unban [PlayerId]
        '''
        await msg.reply(t)

    # @bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
    # async def btn_click_event(b: Bot, e: Event):
    #     """按钮点击事件"""
    #     print(e.target_id)
    #     print('*' * 45)
    #     print(e.body, "\n")
    #
    #     kook_id = e.body['user_id']
    #     value = e.body['value']
    #
    #     q = session.query(DBAdmin).filter(DBAdmin.kookId == kook_id)
    #     z = session.query(literal(True)).filter(q.exists()).scalar()
    #     print(z)
    #     if not z:
    #         await es_channels.command_channel.send("你不是管理员")
    #         return
    #
    #     if value == AdminButtonValue.Refresh_All_VerifyCode:
    #         z = RefreshAllPlayerVerifyCode()
    #         if z:
    #             await es_channels.command_channel.send('刷新所有人验证码成功')
    #     elif value == AdminButtonValue.Show_Last_Match:
    #         await ShowLastMatch()

    @bot.command(name='test_move_old_wait_channel_to_bot_channel', case_sensitive=False, aliases=['test_mowctbc'])
    async def move_from_old_wait_channel_to_x(msg: Message, custom_channel_id: str = ''):
        """
        移动某个频道的玩家到 等候频道
        """
        if msg.author_id != ChannelManager.es_user_id:
            await msg.reply('禁止使用es指令')
            return

        channel: PublicChannel
        if len(custom_channel_id) == 0:
            channel = await bot.client.fetch_public_channel(ChannelManager.old_wait_channel)
        else:
            channel = await bot.client.fetch_public_channel(custom_channel_id)
        k = await channel.fetch_user_list()
        await move_a_to_b_ex(ChannelManager.match_wait_channel, k)
        await msg.reply('成功！')
        pass

    @bot.command(name='move_set_to_wait', case_sensitive=False, aliases=['msw'])
    async def worldO(msg: Message):
        if not check_admin(msg):
            await msg.reply('禁止使用es指令')
            return

        await move_a_to_b(ChannelManager.match_set_channel, ChannelManager.match_wait_channel)

        await msg.reply('移动成功')
        pass

    @bot.command(name='move_to_wait', case_sensitive=False, aliases=['mtw'])
    async def worldO(msg: Message):
        if msg.author_id != ChannelManager.es_user_id:
            await msg.reply('禁止使用es指令')
            return
        # await bot.client.fetch_guild(ChannelManager.sever)
        channel = await bot.client.fetch_public_channel(ChannelManager.match_attack_channel)
        channel_b = await bot.client.fetch_public_channel(ChannelManager.match_wait_channel)
        k = await channel.fetch_user_list()
        for id, user in enumerate(k):
            d: GuildUser = user
            await channel_b.move_user(ChannelManager.match_wait_channel, d.id)

        channel = await bot.client.fetch_public_channel(ChannelManager.match_defend_channel)
        k = await channel.fetch_user_list()
        for id, user in enumerate(k):
            d: GuildUser = user
            await channel_b.move_user(ChannelManager.match_wait_channel, d.id)

        await msg.reply('移动成功')
        pass

    @bot.command(name='move_to_set', case_sensitive=False, aliases=['mtset'])
    async def worldO(msg: Message):
        if msg.author_id != ChannelManager.es_user_id:
            await msg.reply('禁止使用es指令')
            return

        await move_a_to_b(ChannelManager.match_wait_channel, ChannelManager.match_set_channel)

        await msg.reply('移动成功')
        pass

    @bot.command(name='guiltest', case_sensitive=False)
    async def worldO(msg: Message):
        if msg.author_id != ChannelManager.es_user_id:
            await msg.reply('禁止使用es指令')
            return

        await bot.client.fetch_guild(ChannelManager.sever)
        channel = await bot.client.fetch_public_channel(ChannelManager.match_wait_channel)
        channel_b = await bot.client.fetch_public_channel(ChannelManager.match_attack_channel)
        k = await channel.fetch_user_list()
        list_t = []
        for i in k:
            d: GuildUser = i
            list_t.append(d.id)

            await channel_b.move_user(ChannelManager.match_attack_channel, d.id)

    async def check_admin(msg: Message):
        if msg.author_id != ChannelManager.es_user_id or not msg.author_id in ChannelManager.manager_user_id:
            await msg.reply('禁止使用es指令')
            return True
        return False

    async def move_a_to_b(a: str, b: str):
        channel = await bot.client.fetch_public_channel(a)
        channel_b = await bot.client.fetch_public_channel(b)
        k = await channel.fetch_user_list()
        for id, user in enumerate(k):
            d: GuildUser = user
            await channel_b.move_user(ChannelManager.match_wait_channel, d.id)

    async def move_a_to_b_ex(b: str, list_player: list):
        """
        @param:b :频道id
        """
        channel_b = await bot.client.fetch_public_channel(b)
        for id, user_id in enumerate(list_player):
            await channel_b.move_user(b, user_id)


def RefreshAllPlayerVerifyCode():
    # 清空表中的所有记录
    session.execute(text('DELETE FROM PlayerNames'))
    session.commit()

    result = session.query(
        DB_PlayerNames
    ).distinct(DB_PlayerNames.playerId).all()
    player_ids = result
    dict_x = {}
    for i in player_ids:
        player_names_obj: DB_PlayerNames = i
        dict_x[player_names_obj.playerId] = generate_numeric_code()

    for k, v in dict_x.items():
        very = Verify()
        very.playerId = k
        very.code = v
        session.add(very)
    session.commit()
    return True


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

# @bot.command(name='add_admin', case_sensitive=False)
# async def add_admin(msg: Message, kook_id: str):
#     pass


# @bot.command(name='ban', case_sensitive=False)
# async def ban(msg: Message, type: str = 'gi', condition: str = ''):
#     cm = CardMessage()
#
#     type1 = type[1]
#     if type[0] == 'g':
#         if type[1] == 'i':
#             if re.match(r'2\.0\.0\.\d+', condition):
#                 player: Player = sqlSession.query(Player).filter(Player.playerId == condition).first()
#                 if player is not None:
#                     pass
#             else:
#                 await msg.reply(f"guid错误，请仔细检擦{condition}")
#         elif type1 == 'n':
#             p = sqlSession.query(Player).filter(Player.playerId == condition).all()
#             for i in p:
#                 k: Player = i
#                 # cm.append()
#                 pass
#             pass
#     elif True:
#         pass
#     c8 = Card(
#         Module.ActionGroup(
#             Element.Button("临时封印", value='1', click=Types.Click.RETURN_VAL, theme=Types.Theme.INFO),
#             Element.Button("永久封印", value='2', click=Types.Click.RETURN_VAL, theme=Types.Theme.DANGER),
#             Element.Button("封印KOOK", value='3', click=Types.Click.RETURN_VAL, theme=Types.Theme.DANGER),
#             Element.Button("封印Game", value='4', click=Types.Click.RETURN_VAL, theme=Types.Theme.DANGER),
#         )
#     )
#     cm.append(c8)
#     await msg.reply(cm)
#     # sqlSession.commit()
#     # if id_type == 'k':
#     #     record = sqlSession.query(Player).filter(Player.kookId == target_id)
#     # elif id_type == 'g':
#     #     record = sqlSession.query(Player).filter(Player.playerId == target_id)
#     # else:
#     #     record = sqlSession.query(Player).filter(Player.kookId == target_id)
#     #     pass
#     # if record.count() == 1:
#     #     player: Player = record.first()
#     #
#     #     if unit == 'h':
#     #         player.ban_until_time = dt.now() + timedelta(hours=count)
#     #         pass
#     # pass
#     pass
#
#
# @bot.command(name='unban', case_sensitive=False)
# async def unban(msg: Message, id_type: str, target_id: str):
#     if id_type == 'k':
#         record = sqlSession.query(Player).filter(Player.kookId == target_id)
#     elif id_type == 'g':
#         record = sqlSession.query(Player).filter(Player.playerId == target_id)
#     else:
#         record = sqlSession.query(Player).filter(Player.kookId == target_id)
#     pass
