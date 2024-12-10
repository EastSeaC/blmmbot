from khl import Bot

from LogHelper import LogHelper
from blmm_bot import EsChannels
from init_db import get_session
from tables import *

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