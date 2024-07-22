from sqlalchemy import *

from .base import Base


class DB_PlayerChangeNames(Base):
    __tablename__ = "player_change_name"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kookId = Column(VARCHAR(50), unique=True)
    kookName = Column(VARCHAR(50))
    lastKookName = Column(VARCHAR(50))
    playerId = Column(VARCHAR(50), unique=True, nullable=False)

    left_times = Column(Integer, nullable=True, default=0)
