import requests
from khl import Bot, Message, EventTypes, Event, GuildUser, PublicChannel, PublicVoiceChannel
from khl.card import Card, Module, Element, Types, CardMessage, Struct
from sqlalchemy import literal, desc, text

from LogHelper import LogHelper
from kook.ChannelKit import EsChannels
from init_db import get_session
from kook.ChannelKit import ChannelManager
from lib.basic import generate_numeric_code
from match_state import PlayerBasicInfo, MatchState, DivideData
from tables import *
from tables.Admin import DBAdmin
from tables.PlayerNames import DB_PlayerNames

session = get_session()
g_channels: EsChannels


def init(bot: Bot, es_channels: EsChannels):
    global g_channels
    g_channels = es_channels

    @bot.command(name='uca', case_sensitive=False, aliases=['ca', 'xa'])
    async def worldO(msg: Message):
        print("123")
        print(msg.author_id)
        if msg.author_id != ChannelManager.es_user_id:
            await msg.reply('禁止使用es 指令')

            # guild = await bot.client.fetch_guild(ChannelManager.sever)
        wait_channel = await bot.client.fetch_public_channel(ChannelManager.match_wait_channel)
        wait_channel: PublicVoiceChannel = wait_channel
        user_list = await wait_channel.fetch_user_list()
        for i in user_list:
            print(i.id)
        # r = requests.post(UrlHelper.delete_message,
        #                   headers={
        #                       f'Authorization': f"Bot {config['token']}",
        #                   },
        #                   params={
        #                       'msg_id': '8477c586-9111-4312-bc38-a9664d75b32c',
        #                   })
        # print(r.text)
        # print(UrlHelper.delete_message)
        z = await es_channels.command_channel.list_messages()

    @bot.command(name='show_match', case_sensitive=False, aliases=['sm'])
    async def show_match(msg: Message):
        pass

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
