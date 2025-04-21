import re
from random import randint

from khl import Bot, Message, PrivateMessage
from sqlalchemy import or_

from lib.LogHelper import LogHelper
from init_db import get_session
from kook.ChannelKit import EsChannels
from tables import *
from tables.PlayerNames import DB_PlayerNames

session = get_session()
g_channels: EsChannels


# 用于注册命令的函数
def init(bot: Bot, es_channels):
    global g_channels
    g_channels = es_channels

    @bot.command(name='v', case_sensitive=False)
    async def v(msg: Message, player_id: str = '', verify_code: str = '', *args):
        user_id = msg.author_id
        user = await bot.client.fetch_user(user_id)
        LogHelper.log(
            f'注册指令启动: playerId:{player_id}, verify_code:{verify_code}, kookId:{user_id}, kookName:{user.username}')
        failed_text = ''

        if not isinstance(msg, PrivateMessage):
            await msg.delete()

            text = f'(met){user_id}(met): 请私聊注册,以防止泄露关键信息'
            user = await bot.client.fetch_user(user_id)
            # 获取GuildUser对象
            await user.send(text)
            global g_channels
            await g_channels.command_channel.send(text)
            return

        if verify_code == '':
            await msg.reply('验证码不得为空')
            return
        if player_id == '':
            await msg.reply('playerId不得为空')
            return

        # 不应该写精确的数值
        if re.match(r'\d+', player_id):
            player_id = '2.0.0.' + player_id

        if not re.match(r'^[\d\\.]+$', player_id):
            await msg.reply('playerId 不合规则，请重新确认并仔细填写')
            return

        # # 检查 player_id 是否为 17 位
        # pure_digits = re.sub(r'\D', '', player_id)
        # confirm = args[0] if len(args) > 0 else ''
        # if len(pure_digits) != 17:
        #     if confirm.lower() != 'x':
        #         await msg.reply('player_id 不是 17  位，请在命令后添加参数 x 确认注册')
        #         return

        sql_session = get_session()
        z = sql_session.query(DB_PlayerNames).filter(DB_PlayerNames.playerId.like(f'%{player_id}%')).count()
        if z == 0:
            await msg.reply(f'该playerId {player_id} 所属的玩家暂未进入服务器，请先进入游戏服务器')
            return

            # 检测是否已被注册
        t = sql_session.query(DB_Player).filter(
            or_(DB_Player.playerId == player_id, DB_Player.kookId == user_id)).count()
        if t > 0:
            failed_text += '该kook_id 或player_id已被注册,如果你确认这个账号是你的，请联系管理员'
            await msg.reply(failed_text)
            return

        # 判断
        verify_code_obj = sql_session.query(DB_Verify).filter(DB_Verify.code == verify_code,
                                                              DB_Verify.playerId == player_id).first()
        if verify_code_obj is None:
            LogHelper.log(DB_Verify(verify_code_obj).code)
            failed_text += '验证码错误'
            await msg.reply(failed_text)
            return

        player = DB_Player()
        player.playerId = player_id
        player.kookId = user_id
        player.kookName = user.username
        sql_session.add(player)
        sql_session.commit()

        LogHelper.log(f'注册成功, playerId:{player_id}, kookName:{user.username}')
        await msg.reply("注册成功")


def generate_numeric_code(length=6):
    return ''.join([str(randint(0, 9)) for _ in range(length)])

    # @bot.command(name='reg', case_sensitive=False)
# async def world1(msg: Message, player_id: str = '[invalid]'):
#     # 注册命令
#     user_id = msg.author_id
#
#     if re.match(r'\d{17}', player_id):
#         player_id = '2.0.0.' + player_id
#
#     if isinstance(msg, PrivateMessage):
#         text = f'(met){user_id}(met): 请提供正确的player_id'
#         success_text = f'(met){user_id}(met): 验证码已发送到游戏端,请及时查收,并使用/v [验证码] 注册 举例\n /v 6a8473'
#         failed_text = f'(met){user_id}(met):'
#         user = await bot.client.fetch_user(user_id)
#         if player_id == '[invalid]':
#             await user.send(text)
#         elif re.match(r'2\.0\.0\.\d{17}', player_id):
#
#             t = sqlSession.query(Player).filter(
#                 or_(Player.playerId == player_id, Player.kookId == user_id)).count()
#             if t > 0:
#                 failed_text += '该kook_id 或player_id已被注册'
#             else:
#                 t = sqlSession.query(Verify).filter(
#                     or_(Verify.playerId == player_id, Verify.kookId == user_id)).count()
#                 if t > 0:
#                     result = sqlSession.query(Verify).filter(
#                         Verify.until_time < add_minutes_to_current_time(0)
#                     ).all()
#                     for i in result:
#                         sqlSession.delete(i)
#                     sqlSession.commit()
#                     failed_text += '该kook_id 或player_id已请求申请'
#                 else:
#                     verify_one = Verify()
#                     verify_one.playerId = player_id
#                     verify_one.kookId = user_id
#                     verify_one.code = generate_verification_code()
#                     verify_one.until_time = add_minutes_to_current_time()
#                     verify_one.kookName = msg.author.nickname
#                     sqlSession.add(verify_one)
#                     sqlSession.commit()
#
#                     failed_text += '申请成功'
#                 pass
#             await user.send(failed_text)
#             # url = urljoin(urljoin(UrlHelper.reg_url, player_id), msg.author_id)
#             # print(url)
#             # text = await fetch(url)
#             # # r = requests.get(UrlHelper.reg_url + player_id)
#             # result = json.loads(text)
#             # print(result, result['success'])
#             # if result['success']:
#             #     await user.send(success_text)
#             # else:
#             #     failed_text += result['reason']
#             #     await user.send(failed_text)
#         # elif re.match(r'\d{17}', player_id):
#         #     pass
#         # print('zem')
#         # text = await fetch(f'{UrlHelper.reg_url}2.0.0.{player_id}')
#         # result = json.loads(text)
#         # # r = requests.get(f'{UrlHelper.reg_url}2.0.0.{player_id}')
#         # print(result)
#         # if result['success']:
#         #     await user.send(success_text)
#         # else:
#         #     failed_text += result['reason']
#         #     await user.send(failed_text)
#         else:
#             await user.send(text)
#         pass
#         # print(msg)
#     else:
#         await msg.delete()
#
#         text = f'(met){user_id}(met): 请私聊注册,以防止泄露关键信息'
#         user = await bot.client.fetch_user(user_id)
#         # 获取GuildUser对象
#         await user.send(text)
#         # await msg.reply(text)


###################################################################################
# @bot.command(name='v', case_sensitive=False)
# async def validate_player_code(msg: Message, code: str = '!x!'):
#     sqlSession.commit()
#
#     user_id = msg.author_id
#     text = f'(met){user_id}(met): 请提供正确的验证码'
#     f_text = f'(met){user_id}(met):'
#     user = await bot.client.fetch_user(user_id)
#     if code == '!x!':
#         await user.send(text)
#     else:
#         result = sqlSession.query(Verify).filter(
#             and_(Verify.kookId == user_id, Verify.code == code, Verify.until_time >= add_minutes_to_current_time(0)))
#         count = result.count()
#         if count == 1:
#             record: Verify = result.first()
#
#             player = Player()
#             player.playerId = record.playerId
#             player.kookId = user_id
#             player.kookName = record.kookName
#
#             player.admin_level = 0
#             sqlSession.add(player)
#             sqlSession.delete(record)
#             sqlSession.commit()
#
#             f_text += '注册成功'
#         else:
#             k = sqlSession.query(Verify).filter(Verify.until_time < dt.now()).all()
#             # 删除记录
#             for record in k:
#                 sqlSession.delete(record)
#             # 提交事务
#             sqlSession.commit()
#             f_text += '验证码已过期 或 验证码错误，请重新请求'
#         await user.send(f_text)
