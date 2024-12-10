from datetime import datetime

from khl import Bot

from LogHelper import LogHelper
from init_db import get_session
from kook.ChannelKit import EsChannels
from tables import *
from tables.ResetPlayer import DB_ResetPlayer

session = get_session()
g_channels: EsChannels


def init(bot: Bot, es_channels: EsChannels):
    global g_channels
    g_channels = es_channels

    @bot.task.add_cron(minute=49)
    async def reset_all_player_data():
        reset_record = session.query(DB_ResetPlayer).all()
        if not reset_record:
            return
            # 获取今天的日期
        today = datetime.today()
        for i in reset_record:
            reset_player: DB_ResetPlayer = i

            if today.month == reset_player.month and today.day == reset_player.day and not reset_player.is_reset:
                await reset_aux()
                reset_player.is_reset = True

                session.merge(reset_record)

        session.commit()

    async def reset_aux():
        some_records = session.query(DB_PlayerData).all()

        for i in some_records:
            player_data: DB_PlayerData = i
            player_data.refresh_data()
            session.merge(player_data)

        LogHelper.log("已重置所有人数据")
        session.commit()
