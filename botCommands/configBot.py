import os
from datetime import datetime

from khl import Bot

from lib.LogHelper import LogHelper
from init_db import get_session
from kook.ChannelKit import EsChannels
from lib.ServerGameConfig import MapSequence
from lib.SqlUtil.backup_utils import backup
from tables import *
from tables.ResetPlayer import DB_ResetPlayer
from tables.MapRecord import DB_BLMMMap

session = get_session()
g_channels: EsChannels


def init(bot: Bot, es_channels: EsChannels):
    global g_channels
    g_channels = es_channels

    @bot.task.add_cron(hour=9, timezone="Asia/Shanghai")
    async def backup_data():
        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = "C:\\Users\\Administrator\\Desktop\\blmmbackup"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)

        backup_file_path = f"{backup_dir}\\backup_{current_time}.json"
        backup(backup_file_path)
        pass

    # ... existing code ...
    @bot.task.add_cron(second=9, timezone="Asia/Shanghai")
    async def read_map_records():
        try:
            # 假设这里已经导入了必要的模块和类
            with get_session() as session:
                # 查询所有地图记录
                map_records = session.query(DB_BLMMMap.map_name).filter(DB_BLMMMap.is_for_33 == 0,
                                                                        DB_BLMMMap.is_available == 1).scalars().all()

                MapSequence.maps_list = map_records
            # 关闭会话
            session.close()
        except Exception as e:
            print(f"读取地图记录时出错: {e}")

    # ... existing code ...

    @bot.task.add_cron(minute=49, timezone="Asia/Shanghai")
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

                session.merge(reset_player)

        session.commit()

    async def reset_aux():
        session = get_session()
        some_records = session.query(DB_PlayerData).all()

        for i in some_records:
            player_data: DB_PlayerData = i
            player_data.refresh_data()
            session.merge(player_data)

        LogHelper.log("已重置所有人数据")
        session.commit()

    async def reset_apply(arg: str):
        session = get_session()
        some_records = session.query(DB_PlayerData).all()

        if 'a' in arg:
            for i in some_records:
                player_data: DB_PlayerData = i
                player_data.refresh_data_soft()
                session.merge(player_data)
                session.commit()
