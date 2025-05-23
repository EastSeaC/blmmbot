from sqlalchemy import *

from .base import Base

from typing import List
import json


class DB_WillMatchs(Base):
    __tablename__ = "will_matchs"

    id = Column(Integer, primary_key=True, autoincrement=True)  # 自增主键
    time_match = Column(DateTime, nullable=True, default=func.now())  # 对应 C# 的 CreateAt

    # 映射 first_team_player_ids，使用 JSON 字符串存储列表
    first_team_player_ids = Column(Text, nullable=True)  # 存储为 JSON 格式的字符串
    first_team_culture = Column(String(255), nullable=False)  # 对应 C# 的 _firstTeamCultrue

    # 映射 second_team_player_ids，使用 JSON 字符串存储列表
    second_team_player_ids = Column(Text, nullable=True)
    second_team_culture = Column(String(255), nullable=False)

    # MatchType 和 MatchConfig 的枚举映射为字符串存储
    match_type = Column(String(50), nullable=True)  # 对应 C# 的 ESMatchType
    match_config = Column(String(350), nullable=True)  # 对应 C# 的 EMatchConfig

    is_cancel = Column(INT, nullable=True, default='0')  # 对应 C# 的 isCancel
    cancel_reason = Column(Text, nullable=True)
    is_finished = Column(Boolean, nullable=False, default=False)
    finished_time = Column(DateTime, nullable=True)
    match_id = Column(String(255), nullable=True)  # 对应 C# 的 matchId
    server_name = Column(String(255), nullable=True)  # 对应 C# 的 ServerName

    match_id_2 = Column(INT, nullable=False, default=0)
    is_select_mode = Column(INT, nullable=True, default=0)
    map_name = Column(String(255), nullable=True,default='')  # 对应 C# 的 ServerName

    # 方法：转换 JSON 字符串为 Python 列表
    def get_first_team_player_ids(self) -> List[str]:
        return json.loads(self.first_team_player_ids) if self.first_team_player_ids else []

    def add_first_team_player_ids(self, player_id: str):
        player_ids = json.loads(self.first_team_player_ids) if self.first_team_player_ids else []
        player_ids.append(player_id)
        self.first_team_player_ids = json.dumps(player_ids)

    def add_second_team_player_ids(self, player_id: str):
        player_ids = json.loads(self.second_team_player_ids) if self.second_team_player_ids else []
        player_ids.append(player_id)
        self.second_team_player_ids = json.dumps(player_ids)

    def set_first_team_player_ids(self, player_ids: List[str]):
        self.first_team_player_ids = json.dumps(player_ids)

    def get_second_team_player_ids(self) -> List[str]:
        return json.loads(self.second_team_player_ids) if self.second_team_player_ids else []

    def set_second_team_player_ids(self, player_ids: List[str]):
        self.second_team_player_ids = json.dumps(player_ids)

    def get_match_description(self):
        tartest = '未知'
        if self.is_cancel == 1:
            tartest = '已取消'
        elif self.is_finished == 1:
            tartest = '已完成'
        elif self.is_cancel == 0 and self.is_finished == 0:
            tartest = '进行中'
        else:
            tartest = '异常'

        return tartest
        # 将对象转换为字典

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "time_match": self.time_match.isoformat() if self.time_match else None,
            "first_team_player_ids": self.get_first_team_player_ids(),
            "first_team_culture": self.first_team_culture,
            "second_team_player_ids": self.get_second_team_player_ids(),
            "second_team_culture": self.second_team_culture,
            "match_type": self.match_type,
            "match_config": self.match_config,
            "is_cancel": self.is_cancel,
            "cancel_reason": self.cancel_reason,
            "is_finished": self.is_finished,
            "finished_time": self.finished_time.isoformat() if self.finished_time is not None else None,
            "match_id": self.match_id,
            'match_id_2': self.match_id_2,
            "server_name": self.server_name,
        }
