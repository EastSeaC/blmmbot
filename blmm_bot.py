import asyncio
import datetime
import json

import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web
from khl import Bot, Message, GuildUser
from khl.card import Card, Module, Struct, Element, Types, CardMessage
from sqlalchemy import select

from entity.BLMMServerSocket import AsyncSocketServer
from lib.LogHelper import LogHelper
from botCommands import adminBot, regBot, playerBot, configBot, matchBot, testBot, commonBot
from convert.PlayerMatchData import TPlayerMatchData
from init_db import get_session
from kook.ChannelKit import EsChannels, ChannelManager, OldGuildChannel
from lib.ServerManager import ServerManager
from lib.match_guard import MatchGuard
from lib.match_state import MatchConditionEx
from tables.KookChannelGroup import DB_KookChannelGroup
from tables.ScoreLimit import DB_ScoreLimit
from webBlueprint.adminRouter import adminRouter
from webBlueprint.matchRouter import matchRouter

from web_bp import bp

sqlSession = get_session()
# 添加routes到app中
app = web.Application()
app.add_routes(bp)
app.add_routes(adminRouter)
app.add_routes(matchRouter)

guard = MatchGuard()

baseUrl = "https://www.kookapp.cn/api/v3/"
baseUrl2 = "https://www.kookapp.cn"


class UrlHelper:
    baseUrl2 = "https://www.kookapp.cn"

    user_list = baseUrl2 + '/api/v3/channel/user-list'
    move_user = baseUrl2 + '/api/v3/channel/move-user'
    delete_message = baseUrl2 + '/api/v3/message/delete'

    local_url = "http://localhost:14725/"
    reg_url = local_url + 'reg/'


def open_file(path: str):
    """打开path对应的json文件"""
    with open(path, 'r', encoding='utf-8') as f:
        tmp = json.load(f)
    return tmp


# 打开config.json
# config = open_file('config\config.json')
config = open_file('config\\config.json')

# 初始化机器人
"""main bot"""
bot = Bot(token=config['token'])  # 默认采用 websocket

es_channels = EsChannels()


# register command, send `/hello` in channel to invoke
#  case_sensitive=False 忽略大小写
# 分数列表

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


def get_time_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@bot.command(name='help', case_sensitive=False, aliases=['h'])
async def help_x(msg: Message):
    t = '''    /help 或 /h 查看所有指令
    /score_list 或 /sl 查看分数榜单
    /score 或 /s 查看自己的分数
    **(font)/t 或 /type 修改自己的 第一兵种，第二兵种(font)[warning]**
    /change_name 或 /cn 修改名字
    **(font)/e 开启匹配(font)[success]**
    **(font)/cnm (font)[warning]** 【比赛ID】 取消比赛 ，例如 /cnm 10
     
    **(font)注册指令(私聊机器人注册,如果直接私聊机器人，但是无响应，可以先公屏输入/help, 再私聊就可以解决问题)：(font)[warning]**
    /v [playerId] [code]  例如 /v 2.0.0.76561198104994845 600860
    '''
    file_path = 'satic/img/reg-1.png'
    img_url = await bot.client.create_asset(file_path)
    await msg.reply(CardMessage(Card(
        Module.Header('指令说明'),
        Module.Section(
            Struct.Paragraph(
                1,
                Element.Text(t, type=Types.Text.KMD),
            )
        ),
        Module.Container(Element.Image(src=img_url)),
    )))


@bot.task.add_interval(seconds=1)
async def task1():
    # 1s触发器
    # 检查是否有数据
    if MatchConditionEx.end_game:
        MatchConditionEx.end_game = False
        # 移动大伙回来
        await move_a_to_b(ChannelManager.match_attack_channel, ChannelManager.match_wait_channel)
        await move_a_to_b(ChannelManager.match_defend_channel, ChannelManager.match_wait_channel)

        LogHelper.log("输出比赛数据")
        await es_channels.command_channel.send(CardMessage(
            Card(
                Module.Header(f'服务器名称:{MatchConditionEx.server_name}'),
                # Module.Context(f'比赛时间为{MatchConditionEx}'),
                Module.Divider(),
                Module.Header(f'时间:{get_time_str()}'),
                Module.Divider(),
                Module.Header(f'比分:{MatchConditionEx.attacker_score}:{MatchConditionEx.defender_score}')
            )))
        z = MatchConditionEx.data

        name_str = '姓名:'
        game_info = '分数:'
        kill_info = 'KDA伤:'
        for i in z:
            player: TPlayerMatchData = i
            name_str += f'\n{player.truncate_by_width()}'
            game_info += f'\n{player.get_score_info_2}'
            kill_info += f'\n{player.get_kill_info_2}'

        c1 = Card(
            Module.Section(
                Struct.Paragraph(
                    3,
                    Element.Text(name_str, type=Types.Text.KMD),
                    Element.Text(kill_info, type=Types.Text.KMD),
                    Element.Text(game_info, type=Types.Text.KMD),
                )
            )
        )
        await es_channels.command_channel.send(CardMessage(c1))


async def move_a_to_b(a: str, b: str):
    channel = await bot.client.fetch_public_channel(a)
    channel_b = await bot.client.fetch_public_channel(b)
    k = await channel.fetch_user_list()
    for id, user in enumerate(k):
        d: GuildUser = user
        await channel_b.move_user(ChannelManager.match_wait_channel, d.id)


async def move_a_to_b_ex(b: str, list_player: list):
    channel_b = await bot.client.fetch_public_channel(b)
    for id, user_id in enumerate(list_player):
        await channel_b.move_user(b, user_id)


async def CheckDataBase():
    with  get_session() as sql_session:
        result = sql_session.execute(select(DB_ScoreLimit).where(DB_ScoreLimit.score_type == 'default')).first()

        if result is None or len(result) == 0:
            x: DB_ScoreLimit = DB_ScoreLimit()
            sql_session.add(x)
            try:
                sql_session.commit()
            except Exception as e:
                sql_session.rollback()

        result = sql_session.execute(
            select(DB_KookChannelGroup).where(DB_KookChannelGroup.guild_id == OldGuildChannel.sever)).all()
        print('服务器ID', result)
        if len(result) == 0:
            guild = await bot.client.fetch_guild(OldGuildChannel.sever)
            category_list = await guild.fetch_channel_category_list(True)
            current_category_names = [i.name for i in category_list]
            category_names = OldGuildChannel.get_category_list_name()
            for i in category_names:
                if i not in current_category_names:
                    try:

                        blmm_5_category = await guild.create_channel_category(i)
                        channel_group = DB_KookChannelGroup()
                        team_a_channel = await guild.create_voice_channel(OldGuildChannel.channel_a_team,
                                                                          blmm_5_category, )
                        team_b_channel = await guild.create_voice_channel(OldGuildChannel.channel_b_team,
                                                                          blmm_5_category)
                        team_eliminate_channel = await guild.create_voice_channel(
                            OldGuildChannel.channel_eliminate_room, blmm_5_category)
                        channel_group.group_name = i
                        channel_group.group_id = blmm_5_category.id
                        channel_group.guild_id = OldGuildChannel.sever
                        channel_group.team_a_channel = team_a_channel.id
                        channel_group.team_b_channel = team_b_channel.id
                        channel_group.wait_channel = team_eliminate_channel.id
                        try:
                            sql_session.add(channel_group)
                            sql_session.commit()
                        except Exception as e:
                            sql_session.rollback()
                        print('创建服务器 I 频道 成功')
                    except Exception as e:
                        print(e)
        else:
            pass


@bot.on_startup
async def bot_init(bot1: Bot):
    if not es_channels.ready:
        await es_channels.Initial(bot)

    adminBot.init(bot1, es_channels)
    regBot.init(bot1, es_channels)
    playerBot.init(bot1, es_channels)
    configBot.init(bot1, es_channels)
    matchBot.init(bot1, es_channels)
    testBot.init(bot1, es_channels)
    commonBot.init(bot1, es_channels)

    await CheckDataBase()


# 开跑
# 同时运行app和bot
HOST, PORT = '0.0.0.0', 14725
if __name__ == '__main__':
    app.router.add_static('/satic', 'satic')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('satic'))

    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(
            web._run_app(app, host=HOST, port=PORT),
            bot.start(),
            # AsyncSocketServer().start_server(),
        )
    )
