from sqlalchemy import *

from .base import Base


class DB_ScoreLimit(Base):
    __tablename__ = "score_limit"

    id = Column(INT, primary_key=True, nullable=False, autoincrement=True)
    score_type = Column(VARCHAR(50), nullable=False, default='default')

    max_kill_score = Column(INT, nullable=False, default=15)
    min_kill_score = Column(INT, nullable=False, default=0)

    max_death_score = Column(INT, nullable=False, default=12)
    min_death_score = Column(INT, nullable=False, default=0)

    max_assist_score = Column(INT, nullable=False, default=7)
    min_assist_score = Column(INT, nullable=False, default=0)

    max_tk_human_score = Column(INT, nullable=False, default=2)
    min_tk_human_score = Column(INT, nullable=False, default=-5)

    max_tk_hose_score = Column(INT, nullable=False, default=2)
    min_tk_hose_score = Column(INT, nullable=False, default=-4)

    max_multikill_score = Column(INT, nullable=False, default=3)
    min_multikill_score = Column(INT, nullable=False, default=0)

    max_damage_score = Column(INT, nullable=False, default=40)
    min_damage_score = Column(INT, nullable=False, default=0)

    max_codebreaker_score = Column(INT, nullable=False, default=10)
    min_cordbreak_score = Column(INT, nullable=False, default=0)

    failed_minus = Column(INT, nullable=False, default=40)

    per_round_damage = Column(INT, nullable=False, default=1266)

    # 兵种 伤害系数
    InfantryMultiple = Column(Float, nullable=False, default=1.3)
    CavalryMultiple = Column(Float, nullable=False, default=0.95)
    RangerMultiple = Column(Float, nullable=False, default=1.0)
