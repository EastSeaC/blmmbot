from sqlalchemy import *

from .base import Base


class DB_Anouncement(Base):
    __tablename__ = "announcement"

    id = Column(Integer, primary_key=True, autoincrement=True)

    text = Column(VARCHAR(650), unique=True)

    isShow = Column(INT, default=0)

    isForAdmin = Column(INT, default=0)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "is_show": self.isShow == 1,
            "is_for_admin": self.isForAdmin == 1,
        }
