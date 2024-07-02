from sqlalchemy import Column, Integer, VARCHAR
from .base import Base

class DB_PlayerNames(Base):
    __tablename__ = "playernames"

    id = Column(Integer, primary_key=True, autoincrement=True)

    playerId = Column(VARCHAR(50), nullable=False, unique=True)
    PlayerName = Column(VARCHAR(50), nullable=False)
