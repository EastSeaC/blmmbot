import datetime

from sqlalchemy import *

from .base import Base


class ResetPlayer(Base):
    __tablename__ = "reset_player"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timer = Column(DateTime, nullable=False)
    is_reset = Column(Boolean, nullable=False, default=False)
