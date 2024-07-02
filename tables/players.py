import datetime

from sqlalchemy import *

from .base import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    playerId = Column(VARCHAR(50), nullable=False, unique=True)
    kookId = Column(VARCHAR(50), nullable=False, unique=True)
    kookName = Column(VARCHAR(50), nullable=False)

    admin_level = Column(Integer, nullable=False, default=0)
    ban_until_time = Column(DateTime)
    last_login_ip = Column(String(256))

    history_names = Column(JSON, nullable=False, default=[])
    last_change_username_time = Column(DateTime)
    medals = Column(JSON, nullable=False, default=[])

    rank = Column(Integer, nullable=False, default=1000)
    rank_33 = Column(Integer, nullable=False, default=1000)
    preference = Column(Integer, nullable=False, default=0)

    kill = Column(Integer, nullable=False, default=0)
    death = Column(Integer, nullable=False, default=0)
    assist = Column(Integer, nullable=False, default=0)
    match = Column(Integer, nullable=False, default=0)
    win = Column(Integer, nullable=False, default=0)
    lose = Column(Integer, nullable=False, default=0)
    draw = Column(Integer, nullable=False, default=0)
    even = Column(Integer, nullable=False, default=0)

    infantry = Column(Integer, nullable=False, default=0)
    cavalry = Column(Integer, nullable=False, default=0)
    archer = Column(Integer, nullable=False, default=0)

    damage = Column(Integer, nullable=False, default=0)
    team_damage = Column(Integer, nullable=False, default=0)

    def is_banned(self):
        return self.ban_until_time is not None and self.ban_until_time > datetime.datetime.now()

    def to_query_json(self):
        result = {}
        for k, v in self.__dict__.items():
            if k in ("id", "username", "rank", "rank_33", "preference",
                     "kill", "death", "match", "win", "lose", "even", "damage", "team_damage", "medals"):
                result[k] = v

        return

    def to_admin_query_json(self):
        result = {}
        for k, v in self.__dict__.items():
            if k in ("id", "username", "unique_id", "admin_level", "history_names", "last_login_ip"):
                result[k] = v

        result["ban_until_time"] = None if self.ban_until_time is None else self.ban_until_time.strftime(
            "%Y-%m-%d %H:%M:%S")

        return result

    def to_json(self):
        result = {}
        for k, v in self.__dict__.items():
            if k not in ("_sa_instance_state", "salt"):
                result[k] = v

        result[
            "last_change_username_time"] = None if self.last_change_username_time is None else \
            self.last_change_username_time.strftime("%Y-%m-%d %H:%M:%S")
        result["ban_until_time"] = None if self.ban_until_time is None else self.ban_until_time.strftime(
            "%Y-%m-%d %H:%M:%S")

        return result
