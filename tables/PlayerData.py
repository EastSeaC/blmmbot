"""
本表用于保存PlayerId数据，用于玩家没有注释kook时的效果
"""

from sqlalchemy import *

from .base import Base


class DB_PlayerData(Base):
    __tablename__ = "player_data"

    id = Column(Integer, primary_key=True, autoincrement=True)

    playerId = Column(VARCHAR(50), nullable=False, unique=True)
    playerName = Column(VARCHAR(50), nullable=False)

    admin_level = Column(Integer, nullable=False, default=0)
    ban_until_time = Column(DateTime)
    last_login_ip = Column(String(256))

    history_names = Column(JSON, nullable=False, default=[])
    last_change_username_time = Column(DateTime)
    medals = Column(JSON, nullable=False, default=[])

    rank = Column(Integer, nullable=False, default=1000)
    rank_33 = Column(Integer, nullable=False, default=1000)
    preference = Column(Integer, nullable=False, default=0)

    kill = Column(Integer, nullable=False, default=0)
    death = Column(Integer, nullable=False, default=0)
    assist = Column(Integer, nullable=False, default=0)
    # match 为比赛次数
    match = Column(Integer, nullable=False, default=0)
    win = Column(Integer, nullable=False, default=0)
    lose = Column(Integer, nullable=False, default=0)
    draw = Column(Integer, nullable=False, default=0)
    even = Column(Integer, nullable=False, default=0)

    infantry = Column(Integer, nullable=False, default=0)
    cavalry = Column(Integer, nullable=False, default=0)
    archer = Column(Integer, nullable=False, default=0)

    damage = Column(Integer, nullable=False, default=0)
    team_damage = Column(Integer, nullable=False, default=0)

    win_rounds = Column(Integer, nullable=False, default=0)
    fail_rounds = Column(Integer, nullable=False, default=0)
    draw_rounds = Column(Integer, nullable=False, default=0)

    horse_damage = Column(Integer, nullable=False, default=0)
    horse_kill = Column(Integer, nullable=False, default=0)
    horse_tk = Column(Integer, nullable=False, default=0)
    horse_tk_val = Column(Integer, nullable=False, default=0)

    def GetHeaders(self):
        return [
            "player_id",
            "player_name",
            "kill",
            "death",
            "assist",
            "match",
            "win",
            "lose",
            "draw",
            "Infantry",
            "Cavalry",
            "Archer",
            "win_rounds",
            "lose_rounds",
            "draw_rounds",
            "total_rounds",
            "damage",
            "team_damage",
            "tk_times",
            "horse_damage",
            "horse_tk"
        ]
