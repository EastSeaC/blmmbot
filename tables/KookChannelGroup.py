from sqlalchemy import *

from .base import Base

from typing import List
import json


class DB_KookChannelGroup(Base):
    __tablename__ = "kook_channel_group"

    id = Column(Integer, primary_key=True, autoincrement=True)  # 自增主键

    guild_id = Column(BIGINT, default='0')  # 频道服务器id
    group_id = Column(BIGINT, default='0')
    group_name = Column(VARCHAR(50), )
    server_nae = Column(VARCHAR(250))
    wait_channel = Column(BIGINT, default='0')
    team_a_channel = Column(BIGINT, default='0')
    team_b_channel = Column(BIGINT, default='0')

    Eliminate_Wait_Channel = Column(BIGINT, default='0')

    @property
    def get_server_name(self):
        return self.group_name if self.group_name is not None and self.group_name != '' else self.server_nae
