from sqlalchemy import *

from config import INITIAL_SCORE
from convert.PlayerMatchData import TPlayerMatchData
from .base import Base


class DB_MedalPool(Base):
    __tablename__ = "medal_pool"

    id = Column(Integer, primary_key=True, autoincrement=True)
    medalName = Column(VARCHAR(150), nullable=True)

    is_limit_number = Column(INT, nullable=True)
    is_only = Column(INT, nullable=True)

    medal_emoji = Column(Text, nullable=False)
