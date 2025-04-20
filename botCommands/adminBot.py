import datetime
import re

from khl import Bot, Message, GuildUser, PublicChannel, User
from khl.card import Card, Module, Element, Types, CardMessage, Struct
from sqlalchemy import desc, text, select, update

from botCommands.ButtonValueImpl import AdminButtonValue
from config import INITIAL_SCORE
from lib.LogHelper import LogHelper
from blmm_bot import EsChannels
from init_db import get_session
from kook.ChannelKit import ChannelManager
from lib.basic import generate_numeric_code
from tables import *
from tables.Admin import DB_Admin
from tables.Ban import DB_Ban
from tables.PlayerNames import DB_PlayerNames

session = get_session()
g_channels: EsChannels


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

    @bot.command(name='admin_help', case_sensitive=False, aliases=['adh'])
    async def es2(msg: Message):
        t = '''    /reset_state_machine
    
    /admin 打开管理员菜单
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
    /reset_player_score [KookId] 重置玩家分数
        '''
        await msg.reply(t)

    @bot.command(name='reset_server', case_sensitive=False, aliases=['reset'])
    async def reset_game_server(msg: Message, force: str):

        pass

    @bot.command(name='reset_player_score', case_sensitive=False, aliases=['rps'])  # 重置玩家分数
    async def reset_player_score(msg: Message, user_id: str):
        if msg.author_id not in ChannelManager.manager_user_id:
            await msg.reply("禁止使用管理员指令")
            return
        with get_session() as sql_session:
            result = sql_session.execute(select(DB_Player).where(DB_Player.kookId == user_id)).first()
            if result is None or len(result) == 0:
                await msg.reply(f'该账号{user_id}未注册')
                return ""

            player: DB_Player = result[0]
            db_player_data = sql_session.query(DB_PlayerData).filter(DB_PlayerData.playerId == player.playerId)
            # print(db_player_data)
            if db_player_data.count() >= 1:
                db_player: DB_PlayerData = db_player_data.first()
                db_player.rank = INITIAL_SCORE
                player.rank = INITIAL_SCORE

                try:
                    sql_session.merge(db_player)
                    sql_session.merge(player)
                    sql_session.commit()
                    await msg.reply(f'重置{user_id} {player.kookName}分数为{INITIAL_SCORE}')
                except Exception as e:
                    sql_session.rollback()
                    await msg.reply(f'重置 {player.kookName}分数失败')
            else:
                print('wat')

    @bot.command(name='admin', case_sensitive=False)
    async def admin(msg: Message):
        """
        管理员界面
        """
        if msg.author_id not in ChannelManager.manager_user_id:
            await msg.reply("禁止使用管理员指令")
            return

        cm = CardMessage()
        c8 = Card(
            Module.ActionGroup(
                Element.Button("重启服务器1", value=AdminButtonValue.Restart_Server_1,
                               click=Types.Click.RETURN_VAL,
                               theme=Types.Theme.INFO),
                Element.Button("重启服务器2", value=AdminButtonValue.Restart_Server_2,
                               click=Types.Click.RETURN_VAL,
                               theme=Types.Theme.DANGER),
                Element.Button("重启服务器3", value=AdminButtonValue.Restart_Server_3,
                               click=Types.Click.RETURN_VAL,
                               theme=Types.Theme.DANGER),
                Element.Button('查看服务器比赛状态', value=AdminButtonValue.Show_Server_State)
            ),
            Module.Divider(),
            Module.ActionGroup(
                Element.Button("查看组织管理", value=AdminButtonValue.Show_OrganizationPlayers,
                               click=Types.Click.RETURN_VAL,
                               theme=Types.Theme.INFO),
                Element.Button('管理员指令', value=AdminButtonValue.Show_Admin_Command,
                               click=Types.Click.RETURN_VAL,
                               theme=Types.Theme.INFO),

            )
        )
        cm.append(c8)
        await msg.reply(cm)
        pass

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

    @bot.command(name='show', case_sensitive=False, aliases=['sw'])
    async def show_player_info(msg: Message, target_kook_id: str):
        if not ChannelManager.is_es(msg.author_id):
            await msg.reply('禁止使用es指令')
            return

        with get_session() as sql_session:
            p = sql_session.query(DB_Player).filter(DB_Player.kookId == target_kook_id).first()
            if not p:
                await msg.reply(f'该玩家{target_kook_id}未注册')
                return

            player: DB_Player = p
            player_data: DB_PlayerData = sql_session.query(DB_PlayerData).filter(
                DB_PlayerData.playerId == player.playerId).first()
            if not player_data:
                await msg.reply(f'该玩家 player_data not exist')
                return

            target_player_id = player.playerId
            # 查询玩家参与的左侧队伍比赛
            left_matches = sql_session.query(DB_Matchs).filter(DB_Matchs.left_players.contains(target_player_id)).all()
            # 查询玩家参与的右侧队伍比赛
            right_matches = sql_session.query(DB_Matchs).filter(
                DB_Matchs.right_players.contains(target_player_id)).all()

            total_matches = len(left_matches) + len(right_matches)
            win_matches = 0
            draw_matches = 0  # 新增：统计平局场数

            # 统计左侧队伍比赛的胜利场数和平局场数
            for match in left_matches:
                if match.left_win_rounds > match.right_win_rounds:
                    win_matches += 1
                elif match.left_win_rounds == match.right_win_rounds:
                    draw_matches += 1

            # 统计右侧队伍比赛的胜利场数和平局场数
            for match in right_matches:
                if match.right_win_rounds > match.left_win_rounds:
                    win_matches += 1
                elif match.right_win_rounds == match.left_win_rounds:
                    draw_matches += 1

            if total_matches == 0:
                win_rate = 0
                draw_rate = 0
            else:
                win_rate = win_matches / total_matches
                draw_rate = draw_matches / total_matches  # 计算平局率

            cm = CardMessage()
            card = Card(Module.Header(f'kookId:{player.kookName} {player.kookId}'),
                        Module.Divider(),
                        Module.Section(text=f'playerId:{player.playerId}'),
                        Module.Divider(),
                        Module.Section(
                            Struct.Paragraph(
                                3,
                                Element.Text(f'胜率: {win_rate * 100:.2f}%'),
                                Element.Text(f'平局率: {draw_rate * 100:.2f}%')  # 新增：展示平局率
                            ))
                        )
            cm.append(card)
            await msg.reply(cm)
            return
        pass

    @bot.command(name='grant_player_as_admin', case_sensitive=False, aliases=['gad'])
    async def grant_player_as_admin(msg: Message, target_kook_id: str):
        """
        授权管理员，从而能操纵游戏内指令
        """
        if not ChannelManager.is_es(msg.author_id):
            await msg.reply('禁止使用es指令')
            return

        with get_session() as sql_session:
            p = sql_session.query(DB_Player).filter(DB_Player.kookId == target_kook_id)
            if p.count() == 1:
                player: DB_Player = p.first()

                # 当初写成playerId了，要谨慎
                admin_record = sql_session.query(DB_Admin).filter(DB_Admin.kookId == target_kook_id)
                if admin_record.count() >= 1:
                    admin_item: DB_Admin = admin_record.first()
                    if admin_item.can_start_match == 1:
                        await msg.reply('管理员已存在')
                    else:
                        admin_item.can_start_match = 1
                        sql_session.merge(admin_item)
                        sql_session.commit()

                        await msg.reply(f'已成功添加 {admin_item.playerName} 为游戏内管理员')
                else:
                    admin_record = DB_Admin()
                    admin_record.playerId = player.playerId
                    admin_record.kookId = player.kookId
                    admin_record.playerName = player.kookName
                    admin_record.can_start_match = 1

                    sql_session.add(admin_record)
                    sql_session.commit()

                    await msg.reply(f'已成功添加 {admin_record.playerName} 为游戏内管理员')
            else:
                await msg.reply(f'该玩家尚未 注册')

            ChannelManager.organization_user_ids = sql_session.execute(
                select(DB_Admin.kookId).where(DB_Admin.can_start_match == 1)).scalars().all()
        LogHelper.log("更新管理玩家")

    @bot.command(name='remove_grant_as_common', case_sensitive=False, aliases=['rga'])
    async def grant_player_as_admin(msg: Message, target_kook_id: str):
        """
        授权管理员，从而能操纵游戏内指令
        """
        if not ChannelManager.is_es(msg.author_id):
            await msg.reply('禁止使用es指令')

        with get_session() as sql_session:
            p = sql_session.query(DB_Player).filter(DB_Player.kookId == target_kook_id)
            if p.count() != 1:
                await msg.reply('该玩家未注册')
                return

            admin_record = sql_session.query(DB_Admin).filter(DB_Admin.kookId == target_kook_id)
            if admin_record.count() < 1:
                await msg.reply(f'该玩家不是管理员，无需操作')
                return

            admin_item: DB_Admin = admin_record.first()
            if admin_item.can_start_match == 0:
                await msg.reply(f'该玩家不是管理员，无需操作')
                return
            admin_item.can_start_match = 0
            sql_session.merge(admin_item)
            sql_session.commit()

            await msg.reply(f'已移除玩家 {admin_item.playerName} 的管理员 角色')

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

    @bot.command(name='unban', case_sensitive=False, aliases=['uban'])
    async def unban_player_x(msg: Message, kook_id: str):
        if not ChannelManager.is_admin(msg.author_id):
            await msg.reply('禁止使用管理员指令')
            return

        k: User = await bot.client.fetch_user(kook_id)

        with get_session() as sql_session:
            sql_session.execute(
                update(DB_Ban).where(DB_Ban.kookId == kook_id).values(endAt=datetime.datetime.now()))
            sql_session.commit()
            await msg.reply(f'已解除 (met){kook_id}(met) 的封印')

    @bot.command(name='ban', case_sensitive=False)
    async def ban_player(msg: Message, kook_id: str, day: str = '1'):
        if not ChannelManager.is_admin(msg.author_id):
            await msg.reply('禁止使用管理员指令')
            return

        k: User = await bot.client.fetch_user(kook_id)

        if re.match(r'\d+', day):
            real_day = float(day)
        else:
            await msg.reply('时间错误')
            return
        with get_session() as sql_session:
            ban_record = DB_Ban()
            ban_record.kookId = k.id
            ban_record.playerName = k.username
            ban_record.createdAt = datetime.datetime.now()
            ban_record.endAt = datetime.datetime.now() + datetime.timedelta(days=real_day)
            ban_record.admin_kook_id = msg.author_id
            ban_record.admin_kook_name = msg.author.username

            sql_session.add(ban_record)
            sql_session.commit()

            await msg.reply(f'已封印 {ban_record.playerName} {real_day}天')

    @bot.command(name='add_score', case_sensitive=False)
    async def add_score(msg: Message, kook_id: str, score: str):
        if not ChannelManager.is_admin(msg.author_id):
            await msg.reply('禁止使用管理员指令')
            return

        # 参数检查
        real_score = 0
        if re.match(r'-?\d+', score):
            real_score = int(score)
        else:
            await msg.reply('输入分数错误')
            return

        with get_session() as sql_session:
            x = sql_session.query(DB_Player).filter(DB_Player.kookId == kook_id)

            if x.count() == 0:
                await msg.reply('该用户未注册')
                return

            player: DB_Player = x.first()

            player_data: DB_PlayerData = sql_session.query(DB_PlayerData).filter(
                DB_PlayerData.playerId == player.playerId).first()
            old_rank = player_data.rank
            player_data.rank += real_score
            sql_session.merge(player_data)
            sql_session.commit()

            await msg.reply(f'(met){kook_id}(met) 分数 {old_rank}->{player_data.rank}')

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
        very = DB_Verify()
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
