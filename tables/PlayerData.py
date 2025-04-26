"""
本表用于保存PlayerId数据，用于玩家没有注释kook时的效果
"""

from sqlalchemy import *

from config import INITIAL_SCORE
from convert.PlayerMatchData import TPlayerMatchData
from .base import Base


class DB_PlayerData(Base):
    __tablename__ = "player_data"

    id = Column(Integer, primary_key=True, autoincrement=True)

    playerId = Column(VARCHAR(50), nullable=False, unique=True)
    playerName = Column(VARCHAR(50), nullable=True)

    admin_level = Column(Integer, nullable=False, default=0)
    create_time = Column(DateTime)
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

    def add_match_data(self, match_data: TPlayerMatchData):
        self.win += match_data.win
        self.lose += match_data.lose
        self.draw += match_data.draw_rounds

        self.infantry += match_data.Infantry
        self.cavalry += match_data.Cavalry
        self.archer += match_data.Archer

        self.damage += match_data.damage
        self.team_damage += match_data.team_damage

        self.win_rounds += match_data.win_rounds
        self.fail_rounds += match_data.lose_rounds
        self.draw_rounds += match_data.draw_rounds

        self.horse_damage += match_data.horse_damage

        self.kill += match_data.kill
        self.death += match_data.death
        self.assist += match_data.assist
        self.match += 1

        self.win += 0 if match_data.is_lose else 1
        self.lose += 1 if match_data.is_lose else 0
        pass

    def refresh_data_soft(self):
        self.rank = self.rank if self.rank >= INITIAL_SCORE else INITIAL_SCORE
        self.rank_33 = (self.rank_33 - INITIAL_SCORE) / 2
        self.preference = 0

        self.kill = 0
        self.death = 0
        self.assist = 0
        # match 为比赛次数
        self.match = 0
        self.win = 0
        self.lose = 0
        self.draw = 0
        self.even = 0

        self.infantry = 0
        self.cavalry = 0
        self.archer = 0

        self.damage = 0
        self.team_damage = 0

        self.win_rounds = 0
        self.fail_rounds = 0
        self.draw_rounds = 0

        self.horse_damage = 0
        self.horse_kill = 0
        self.horse_tk = 0
        self.horse_tk_val = 0

    def refresh_data(self):
        self.rank = (self.rank - INITIAL_SCORE) / 2
        self.rank_33 = (self.rank_33 - INITIAL_SCORE) / 2
        self.preference = 0

        self.kill = 0
        self.death = 0
        self.assist = 0
        # match 为比赛次数
        self.match = 0
        self.win = 0
        self.lose = 0
        self.draw = 0
        self.even = 0

        self.infantry = 0
        self.cavalry = 0
        self.archer = 0

        self.damage = 0
        self.team_damage = 0

        self.win_rounds = 0
        self.fail_rounds = 0
        self.draw_rounds = 0

        self.horse_damage = 0
        self.horse_kill = 0
        self.horse_tk = 0
        self.horse_tk_val = 0

    def clear_data(self):
        self.rank = INITIAL_SCORE
        self.rank_33 = INITIAL_SCORE
        self.preference = 0

        self.kill = 0
        self.death = 0
        self.assist = 0
        # match 为比赛次数
        self.match = 0
        self.win = 0
        self.lose = 0
        self.draw = 0
        self.even = 0

        self.infantry = 0
        self.cavalry = 0
        self.archer = 0

        self.damage = 0
        self.team_damage = 0

        self.win_rounds = 0
        self.fail_rounds = 0
        self.draw_rounds = 0

        self.horse_damage = 0
        self.horse_kill = 0
        self.horse_tk = 0
        self.horse_tk_val = 0

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
