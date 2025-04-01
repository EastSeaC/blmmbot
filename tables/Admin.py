from sqlalchemy import *

from .base import Base


class DB_Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kookId = Column(VARCHAR(50), unique=True)
    kookName = Column(VARCHAR(50))
    playerId = Column(VARCHAR(50), unique=True, nullable=False)
    playerName = Column(VARCHAR(50), nullable=False)

    priority = Column(Integer, nullable=True)
