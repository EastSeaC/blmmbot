# ... existing code ...
from sqlalchemy import Column, Integer, VARCHAR, INT

from tables import Base


class DB_BLMMMap(Base):
    __tablename__ = "blmm_map"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 假设地图名称，唯一标识地图
    map_name = Column(VARCHAR(255), unique=True)
    # 假设地图描述
    description = Column(VARCHAR(650))
    # 假设地图是否可用
    is_available = Column(INT, default=0)

    is_for_33 = Column(INT, nullable=True, default=0)

    def to_dict(self) -> dict:
        return {
            "map_name": self.map_name,
            "description": self.description,
            "is_available": self.is_available == 1,
            'is_for_33': self.is_for_33 == 1,
        }

# ... existing code ...
