from sqlalchemy import *

from .base import Base


class DB_Ban(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kookId = Column(VARCHAR(50), unique=True)
    kookName = Column(VARCHAR(50), nullable=True)
    playerId = Column(VARCHAR(50), unique=True, nullable=True)
    playerName = Column(VARCHAR(50), nullable=True)

    banType = Column(VARCHAR(50), nullable=True)
    createdAt = Column(DATETIME, default='now()')
    endAt = Column(DATETIME, default='now()')

    admin_kook_id = Column(VARCHAR(50), unique=True, nullable=True)
    admin_kook_name = Column(VARCHAR(50), nullable=True)
    admin_playerId = Column(VARCHAR(50), unique=True, nullable=True)
    admin_playerName = Column(VARCHAR(50), nullable=True)
