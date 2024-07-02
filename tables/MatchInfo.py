from sqlalchemy import *

from .base import Base


class DB_Matchs(Base):
    __tablename__ = "blmmmatchs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    time_match = Column(DateTime, nullable=True, default=func.now())

    left_players = Column(JSON, nullable=True, default='{}')
    right_players = Column(JSON, nullable=True, default='{}')

    left_scores = Column(Integer, nullable=True, default=0)
    right_scores = Column(Integer, nullable=True, default=0)

    left_win_rounds = Column(Integer, nullable=True, default=0)
    right_win_rounds = Column(Integer, nullable=True, default=0)

    mvp_player = Column(JSON, nullable=True, default='{}')

    tag = Column(VARCHAR(50), nullable=True, default='Test')

    raw = Column(JSON, nullable=False, default='{}')

    server_name = Column(VARCHAR(30), nullable=True, default='btl1')

    def get_data(self):
        return {
            'id': self.id,
            'time_match': self.time_match.strftime("%Y-%m-%d %H:%M:%S"),
            'left_players': self.left_players,
            'right_players': self.right_players,
            'left_scores': self.left_scores,
            'right_scores': self.right_scores,
            'left_win_rounds': self.left_win_rounds,
            'right_win_rounds': self.right_win_rounds,
            'mvp_player': self.mvp_player,
            'tag': self.tag,
        }
