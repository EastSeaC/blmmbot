import asyncio
import datetime
import json
import re
from random import randint

import aiohttp
import aiohttp_jinja2
import jinja2
import requests
from aiohttp import web
from khl import Bot, Message, Event, EventTypes, GuildUser
from khl.card import Card, Module, Types, Element, Struct, CardMessage

from LogHelper import LogHelper
from botCommands import adminBot, regBot
from init_db import get_session
from kook.ChannelKit import EsChannels, ChannelManager
from match_guard import MatchGuard
from match_state import MatchState, MatchCondition, PlayerInfo
from tables import *
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
config = open_file('config\config.json')

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
    /reg [player_id] 注册指令 例如 /reg 2.0.0.xxxxxxxxxx
    /v [code] 回复验证码 例如 /v 6axdee

    /spniwc  查看当前等候频道里的玩家有
    /reset_state_machine
    
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
    /show_match 显示已有对局   
    '''
    await msg.reply(t)


@bot.command(name='score_list', case_sensitive=False, aliases=['sl'])
async def world(msg: Message):
    cm = CardMessage()

    sqlSession.commit()
    t = sqlSession.query(Player).order_by(Player.rank.desc()).limit(10).all()
    print(t)
    kill_scoreboard = '**积分榜单**'
    for id, k in enumerate(t):
        player: Player = k
        kill_scoreboard += f"\n{player.kookName}:{player.rank}"

    game_scoreboard = '**对局榜单**'
    t = sqlSession.query(Player).order_by(Player.win.desc()).limit(10).all()
    for id, k in enumerate(t):
        player: Player = k
        game_scoreboard += f"\n{player.kookName}:{player.win}"

    c2 = Card(
        Module.Section(
            Struct.Paragraph(
                3,
                Element.Text(kill_scoreboard, type=Types.Text.KMD),
                Element.Text(game_scoreboard, type=Types.Text.KMD),
                Element.Text(f"**步/骑/弓弩**\n",
                             type=Types.Text.KMD),
            )
        )
    )
    cm.append(c2)
    await msg.reply(cm)


@bot.command(name='score', case_sensitive=False, aliases=['s'])
async def show_score(msg: Message):
    sqlSession.commit()
    t = sqlSession.query(Player).filter(Player.kookId == msg.author_id)
    if t.count() == 1:
        player: Player = t.first()
        cm = CardMessage()
        c1 = Card(
            Module.Header("等级"),
            Module.Section(str(player.rank))
        )
        Kill_Info = f'''**Kill Info**
Kills:{player.kill}
Deaths:{player.death}
Assists:{player.assist}
KDA:{(player.kill + player.assist) / max(player.death, 1)}
KD: {player.kill / max(player.death, 1)}
'''

        game_info = f'''**游戏**
对局数:{player.match}
胜场:{player.win}
败场:{player.lose}
平局:{player.draw}
胜/败:{player.win / max(player.lose, 1)}
MVPs:{0}
        '''
        c2 = Card(
            Module.Section(
                Struct.Paragraph(
                    3,
                    Element.Text(Kill_Info, type=Types.Text.KMD),
                    Element.Text(game_info, type=Types.Text.KMD),
                    Element.Text(f"**步/骑/弓弩**\n{player.infantry}/{player.cavalry}/{player.archer}",
                                 type=Types.Text.KMD),
                )
            )
        )
        # cm.append(c1)
        cm.append(c1)
        cm.append(c2)
        await  msg.reply(cm)
    else:
        await msg.reply("请先注册")

    pass


@bot.command(name='add_admin', case_sensitive=False)
async def add_admin(msg: Message, kook_id: str):
    pass


@bot.command(name='ban', case_sensitive=False)
async def ban(msg: Message, type: str = 'gi', condition: str = ''):
    cm = CardMessage()

    type1 = type[1]
    if type[0] == 'g':
        if type[1] == 'i':
            if re.match(r'2\.0\.0\.\d+', condition):
                player: Player = sqlSession.query(Player).filter(Player.playerId == condition).first()
                if player is not None:
                    pass
            else:
                await msg.reply(f"guid错误，请仔细检擦{condition}")
        elif type1 == 'n':
            p = sqlSession.query(Player).filter(Player.playerId == condition).all()
            for i in p:
                k: Player = i
                # cm.append()
                pass
            pass
    elif True:
        pass
    c8 = Card(
        Module.ActionGroup(
            Element.Button("临时封印", value='1', click=Types.Click.RETURN_VAL, theme=Types.Theme.INFO),
            Element.Button("永久封印", value='2', click=Types.Click.RETURN_VAL, theme=Types.Theme.DANGER),
            Element.Button("封印KOOK", value='3', click=Types.Click.RETURN_VAL, theme=Types.Theme.DANGER),
            Element.Button("封印Game", value='4', click=Types.Click.RETURN_VAL, theme=Types.Theme.DANGER),
        )
    )
    cm.append(c8)
    await msg.reply(cm)
    # sqlSession.commit()
    # if id_type == 'k':
    #     record = sqlSession.query(Player).filter(Player.kookId == target_id)
    # elif id_type == 'g':
    #     record = sqlSession.query(Player).filter(Player.playerId == target_id)
    # else:
    #     record = sqlSession.query(Player).filter(Player.kookId == target_id)
    #     pass
    # if record.count() == 1:
    #     player: Player = record.first()
    #
    #     if unit == 'h':
    #         player.ban_until_time = dt.now() + timedelta(hours=count)
    #         pass
    # pass
    pass


@bot.command(name='unban', case_sensitive=False)
async def unban(msg: Message, id_type: str, target_id: str):
    if id_type == 'k':
        record = sqlSession.query(Player).filter(Player.kookId == target_id)
    elif id_type == 'g':
        record = sqlSession.query(Player).filter(Player.playerId == target_id)
    else:
        record = sqlSession.query(Player).filter(Player.kookId == target_id)
    pass


@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def confirm_ban(b: Bot, e: Event):
    pass


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
                          'msg_id': 'a69d7d69-08c7-4e32-9e72-c87ff68ae3a4',
                      })
    print(r.text)
    print(UrlHelper.delete_message)
    # z = await es_channels.command_channel.list_messages()
    #
    # for i in z["items"]:
    #     print(i['id'])
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


# 开跑
# 同时运行app和bot
HOST, PORT = 'localhost', 14725
if __name__ == '__main__':
    app.router.add_static('/satic', 'satic')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('satic'))
    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(web._run_app(app, host=HOST, port=PORT), bot.start()))
