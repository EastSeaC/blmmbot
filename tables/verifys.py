from sqlalchemy import *

from .base import Base


class Verify(Base):
    __tablename__ = "verifys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    playerId = Column(VARCHAR(50), nullable=False, unique=True)

    code = Column(VARCHAR(20), nullable=False)
