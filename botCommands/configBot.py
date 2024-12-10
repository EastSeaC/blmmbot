from khl import Bot, Message, EventTypes, Event, GuildUser, PublicChannel
from khl.card import Card, Module, Element, Types, CardMessage, Struct
from sqlalchemy import literal, desc, text

from LogHelper import LogHelper
from blmm_bot import EsChannels
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

    @bot.task.add_interval(days=1)
    async def reset_all_player_data():
        some_records = session.query(DB_PlayerData).all()

        for i in some_records:
            player_data: DB_PlayerData = i
            player_data.refresh_data()
            session.merge(player_data)

        LogHelper.log("已重置所有人数据")
        session.commit()