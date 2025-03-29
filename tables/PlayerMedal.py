"""
"""

from sqlalchemy import *

from config import INITIAL_SCORE
from convert.PlayerMatchData import TPlayerMatchData
from .base import Base


class DB_PlayerMedal(Base):
    __tablename__ = "player_medal"

    id = Column(Integer, primary_key=True, autoincrement=True)

    playerId = Column(VARCHAR(50), nullable=True, unique=True)
    playerName = Column(VARCHAR(50), nullable=True)
    kookId = Column(VARCHAR(50), nullable=False, unique=True)

    medal_blmm_testor = Column(INT, nullable=False)

    __base_emoji = "(emj){}(emj)[{}]"

    @property
    def get_testor_emoji(self):
        if self.medal_blmm_testor == 1:
            return DB_PlayerMedal.__base_emoji.format('BLMM元勋', '9019084812125033/4ggrfAXKOo02o02o')
        else:
            return ''
