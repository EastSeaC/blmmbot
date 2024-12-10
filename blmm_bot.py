import asyncio
import datetime
import json

import aiohttp
import aiohttp_jinja2
import jinja2
import requests
from aiohttp import web
from khl import Bot, Message, Event, EventTypes, PublicVoiceChannel, GuildUser
from khl.card import Card, Module, Struct, Element, Types, CardMessage

from LogHelper import LogHelper
from botCommands import adminBot, regBot, playerBot
from convert.PlayerMatchData import TPlayerMatchData
from init_db import get_session
from kook.ChannelKit import EsChannels, ChannelManager
from match_guard import MatchGuard
from match_state import MatchState, MatchCondition, MatchConditionEx
from webBlueprint.adminRouter import adminRouter
from web_bp import bp

sqlSession = get_session()
# 添加routes到app中
app = web.Application()
app.add_routes(bp)
app.add_routes(adminRouter)
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


@bot.command(name='help', case_sensitive=False, aliases=['h'])
async def help_x(msg: Message):
    t = '''/help 查看所有指令
    /score_list /sl 查看分数榜单
    /score /s 查看自己的分数
    /change_name /cn 修改名字
    **(font)/e 开启匹配(font)[success]**
     
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

    # data = {'target_id': ChannelManager.match_set_channel, 'array': json.dumps(list_t)}
    # requests.post(UrlHelper.move_user, data)
    # await msg.reply('移动成功')
    # pass
    # guild = await bot.client.fetch_guild(ChannelManager.sever)
    # rolse = await guild.fetch_roles()
    # for i in rolse:
    #     print(i.name)


@bot.command(name='uca', case_sensitive=False, aliases=['ca', 'xa'])
async def worldO(msg: Message):
    if msg.author_id != ChannelManager.es_user_id:
        await msg.reply('禁止使用es 指令')
        return
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


@bot.command(name='show_match', case_sensitive=False, aliases=['sm'])
async def show_match(msg: Message):
    pass


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
            )))
        z = MatchConditionEx.data

        name_str = '姓名:'
        game_info = '分数:'
        kill_info = 'KDA:'
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


@bot.task.add_interval(seconds=3)
async def task5():
    condition = stateMachine.check_state()
    if condition == MatchCondition.WaitingJoin:
        z: PublicVoiceChannel = es_channels.wait_channel
        user_list: list = await z.fetch_user_list()
        user_count = len(user_list)
        if user_count >= 12:
            pass
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
        stateMachine.remove_player_from_wait_list(user_id=user_id)
        await es_channels.command_channel.send(f'1名玩家 离开等候频道，还剩下{stateMachine.get_match_num}')
        pass
    elif (channel_id == ChannelManager.match_attack_channel) or (channel_id == ChannelManager.match_defend_channel):
        warning_state, times = guard.add_warning_times(user_id)
        if warning_state:
            pass
        warning_text = f'(met){user_id}(met): 请注意,你已离开比赛频道{times}次'
        # 获取指定频道
        ch = await bot.client.fetch_public_channel(ChannelManager.announcement)
        ret = await ch.send(warning_text)  # 方法1
        # LogHelper.log(f" {ret['msg_id']}")  # 方法1 发送消息的id
        pass


@bot.on_startup
async def bot_init(bot1: Bot):
    if not es_channels.ready:
        await es_channels.Initial(bot)

    adminBot.init(bot1, es_channels)
    regBot.init(bot1, es_channels)
    playerBot.init(bot1, es_channels)


# 开跑
# 同时运行app和bot
HOST, PORT = '0.0.0.0', 14725
if __name__ == '__main__':
    app.router.add_static('/satic', 'satic')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('satic'))
    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(web._run_app(app, host=HOST, port=PORT), bot.start()))
