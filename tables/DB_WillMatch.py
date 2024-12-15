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
    first_team_culture = Column(String(255), nullable=True)  # 对应 C# 的 _firstTeamCultrue

    # 映射 second_team_player_ids，使用 JSON 字符串存储列表
    second_team_player_ids = Column(Text, nullable=True)

    # MatchType 和 MatchConfig 的枚举映射为字符串存储
    match_type = Column(String(50), nullable=True)  # 对应 C# 的 ESMatchType
    match_config = Column(String(350), nullable=True)  # 对应 C# 的 EMatchConfig

    is_cancel = Column(Boolean, nullable=True, default=False)  # 对应 C# 的 isCancel
    cancel_reason = Column(Text, nullable=True)
    is_finished = Column(Boolean, nullable=False, default=False)
    finished_time = Column(DateTime, nullable=True)
    match_id = Column(String(255), nullable=True)  # 对应 C# 的 matchId
    server_name = Column(String(255), nullable=True)  # 对应 C# 的 ServerName

    # 方法：转换 JSON 字符串为 Python 列表
    def get_first_team_player_ids(self) -> List[str]:
        return json.loads(self.first_team_player_ids) if self.first_team_player_ids else []

    def set_first_team_player_ids(self, player_ids: List[str]):
        self.first_team_player_ids = json.dumps(player_ids)

    def get_second_team_player_ids(self) -> List[str]:
        return json.loads(self.second_team_player_ids) if self.second_team_player_ids else []

    def set_second_team_player_ids(self, player_ids: List[str]):
        self.second_team_player_ids = json.dumps(player_ids)
