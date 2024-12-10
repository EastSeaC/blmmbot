import datetime

from sqlalchemy import *

from .base import Base


class DB_ResetPlayer(Base):
    __tablename__ = "reset_player"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timer = Column(DateTime, nullable=False)
    is_reset = Column(Boolean, nullable=False, default=False)

    month = Column(Integer, nullable=False, default=1)
    day = Column(Integer, nullable=False, default=1)
