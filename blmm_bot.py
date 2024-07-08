import asyncio
import datetime
import json
from random import randint

import aiohttp
import aiohttp_jinja2
import jinja2
import requests
from aiohttp import web
from khl import Bot, Message, Event, EventTypes, GuildUser
from khl.card import Card, Module, Struct, Element, Types, CardMessage

from LogHelper import LogHelper
from botCommands import adminBot, regBot, playerBot
from config import get_rank_name
from convert.PlayerMatchData import TPlayerMatchData
from init_db import get_session
from kook.ChannelKit import EsChannels, ChannelManager
from match_guard import MatchGuard
from match_state import MatchState, MatchCondition, PlayerInfo, MatchConditionEx
from tables import DB_Matchs
from web_bp import bp

sqlSession = get_session()
# 添加routes到app中
app = web.Application()
app.add_routes(bp)

stateMachine = MatchState()
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


@bot.command(name='help', case_sensitive=False)
async def help_x(msg: Message):
    t = '''
    /help 查看所有指令

    /score_list /sl 查看分数榜单
    /score /s 查看自己的分数
    
    注册指令：
    /v [playerId] [code]  例如 /v 2.0.0.xxxxxxxxxx 600860

    /spniwc  查看当前等候频道里的玩家有

    /show_match 显示已有对局   
    '''
    await msg.reply(t)


@bot.command(name='show_player_numbers_in_waiting_channel', case_sensitive=False, aliases=['spniwc', 'spn'])
async def show_player_numbers_in_waiting_channel(msg: Message):
    # 查看在等候频道里的玩家
    await msg.reply('当前等候频道里的玩家有:' + str(stateMachine.player_number))


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


@bot.command(name='reac', case_sensitive=False)
async def worldO(msg: Message):
    # 公告区
    ch = await bot.client.fetch_public_channel(ChannelManager.announcement)
    # 使用channel对象的send
    ret = await ch.send("这是一个测试信息,使用了ch.send")  # 方法1

    # 往其他频道发送信息
    # 使用bot对象的client.send
    # ret = await bot.client.send(ch, "这是一个测试信息，使用了bot.client.send")  # 方法2
    # print(f"bot.client.send | msg_id {ret['msg_id']}")  # 方法2 发送消息的id
    # await msg.reply('')


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

    # data = {'target_id': ChannelManager.match_set_channel, 'array': json.dumps(list_t)}
    # requests.post(UrlHelper.move_user, data)
    # await msg.reply('移动成功')
    # pass
    # guild = await bot.client.fetch_guild(ChannelManager.sever)
    # rolse = await guild.fetch_roles()
    # for i in rolse:
    #     print(i.name)


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


@bot.command(name='rtc', case_sensitive=False, aliases=['yc'])
async def tojadx(msg: Message):
    if msg.author_id != ChannelManager.es_user_id:
        await msg.reply('禁止使用es指令')
        return

    channel = await bot.client.fetch_public_channel(ChannelManager.match_wait_channel)
    k = await channel.fetch_user_list()
    player_list = []
    for id, user in enumerate(k):
        t: GuildUser = user
        player_list.append(PlayerInfo(
            {'score': randint(10, 20), 'user_id': t.id}))
    if len(player_list) % 2 != 0:
        player_list.pop()

    x, y = stateMachine.divide_player_test(player_list)
    await move_a_to_b_ex(ChannelManager.match_attack_channel, x)
    await move_a_to_b_ex(ChannelManager.match_defend_channel, y)
    await msg.reply('over!+')


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


@bot.command(name='move_set_to_wait', case_sensitive=False, aliases=['msw'])
async def worldO(msg: Message):
    if msg.author_id != ChannelManager.es_user_id:
        await msg.reply('禁止使用es指令')
        return

    await move_a_to_b(ChannelManager.match_set_channel, ChannelManager.match_wait_channel)

    await msg.reply('移动成功')
    pass


@bot.command(name='uca', case_sensitive=False, aliases=['ca', 'xa'])
async def worldO(msg: Message):
    # guild = await bot.client.fetch_guild(ChannelManager.sever)
    r = requests.post(UrlHelper.delete_message,
                      headers={
                          f'Authorization': f"Bot {config['token']}",
                      },
                      params={
                          'msg_id': '8477c586-9111-4312-bc38-a9664d75b32c',
                      })
    print(r.text)
    print(UrlHelper.delete_message)
    z = await es_channels.command_channel.list_messages()

    for i in z["items"]:
        print(i['id'])
        print(i)
        print(type(z))
        break
    #     r = requests.post(UrlHelper.delete_message,
    #                       headers={
    #                           f'Authorization': f"Bot {config['token']}",
    #                       },
    #                       params={
    #                           'msg_id': i['id'],
    #                       })
    #     print(r.text)
    # # 真是结果
    # result = json.loads(r.text)
    # data: list = result['data']
    # print(data)
    # print(len(data))
    # break


@bot.command(name='show_match', case_sensitive=False, aliases=['sm'])
async def show_match(msg: Message):
    # x

    pass


# 1s触发器


@bot.task.add_interval(seconds=1)
async def task1():
    # 检查是否有数据
    if MatchConditionEx.state:
        MatchConditionEx.state = False
        LogHelper.log("输出比赛数据")
        await es_channels.command_channel.send(CardMessage(Card(Module.Divider())))
        z = MatchConditionEx.data

        score_str = ''
        KD_str = ''
        name_str = '姓名:'
        for i in z:
            player: TPlayerMatchData = i
            name_str += f'\n{player.player_name}'
            kill_info = \
                f'''战场表现:
Kills:{player.kill}
Deaths:{player.death}
KDA:{(player.kill + player.assist) / max(player.death, 1)}
KD: {player.kill / max(player.death, 1)}
伤害/TK: {player.damage}/{player.team_damage}
'''
            game_info = f'''**游戏**
对局数:{player.match}
胜场:{player.win}
败场:{player.lose}
平局:{player.draw}
胜/败:{player.win / max(player.lose, 1)}
MVPs:{0}'''
            c1 = Card(
                Module.Header(f"名称:{player.player_name}\tUID:{player.player_id}"),
                Module.Context(
                    f"得分: (font){+40}(font)[success]"
                ),
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(kill_info, type=Types.Text.KMD),
                        Element.Text(game_info, type=Types.Text.KMD),
                        Element.Text(f"位阶:\n{get_rank_name(1000)}", type=Types.Text.KMD),
                    )
                )
            )
            await es_channels.command_channel.send(CardMessage(c1))
        # 添加名字
        #
        # c1 = Card(
        #     Module.Header("胜者组"),
        #     Module.Section(
        #         Struct.Paragraph(
        #             3,
        #             Element.Text(f"名字:\n{}",type=Types.Text.KMD),
        #             Element.Text(f"分数:\n{player.rank}", type=Types.Text.KMD),
        #             Element.Text(f"位阶:\n{get_rank_name(player.rank)}", type=Types.Text.KMD),
        #         )
        #     )
        # )

    if not es_channels.ready:
        await es_channels.Initial(bot)

    # 定时器
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
        # channel = await bot.client.fetch_public_channel(ChannelManager.command_channel)
        z = "当前状态为 等待玩家加入"
        # LogHelper.log(z)
        # await  es_channels.command_channel.send(z)
    elif condition == MatchCondition.DividePlayer:
        z = "当前状态为 划分玩家状态"
        # LogHelper.log(z)

        # await es_channels.command_channel.send(z)
    pass


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
        pass
    elif (channel_id == ChannelManager.match_attack_channel) or (channel_id == ChannelManager.match_defend_channel):
        warning_state, times = guard.add_warning_times(user_id)
        if warning_state:
            pass
        warning_text = f'(met){user_id}(met): 请注意,你已离开比赛频道{times}次'
        # 获取指定频道
        ch = await bot.client.fetch_public_channel(ChannelManager.announcement)
        ret = await ch.send(warning_text)  # 方法1
        print(f"ch.send | msg_id {ret['msg_id']}")  # 方法1 发送消息的id
        pass


@bot.on_startup
async def bot_init(bot1: Bot):
    adminBot.init(bot1, es_channels)
    regBot.init(bot1, es_channels)
    playerBot.init(bot1, es_channels)


# 开跑
# 同时运行app和bot
HOST, PORT = 'localhost', 14725
if __name__ == '__main__':
    app.router.add_static('/satic', 'satic')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('satic'))
    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(web._run_app(app, host=HOST, port=PORT), bot.start()))
