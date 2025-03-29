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
