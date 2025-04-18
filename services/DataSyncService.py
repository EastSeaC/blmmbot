from init_db import get_session
from tables import DB_Player, DB_PlayerData
from tables.Admin import DB_Admin

from sqlalchemy.orm import class_mapper

from tables.PlayerNames import DB_PlayerNames
from tables.WillMatch import DB_WillMatchs
from sqlalchemy import or_  # 导入 or_ 函数


def safe_deserialize(model_class, data_dict):
    """安全反序列化，忽略不存在的字段"""
    mapper = class_mapper(model_class)
    valid_keys = {c.key for c in mapper.columns}
    filtered_data = {k: v for k, v in data_dict.items() if k in valid_keys}
    return model_class(**filtered_data)


def serialize(model):
    columns = [c.key for c in class_mapper(model.__class__).columns]
    return dict((c, getattr(model, c)) for c in columns)


class DataSyncService:
    @classmethod
    def get_admin(cls):
        with get_session() as session:
            list_of_admin = session.query(DB_Admin).all()
            return [serialize(admin) for admin in list_of_admin]

    @classmethod
    def get_sync(cls):
        with get_session() as session:
            list_of_admin = session.query(DB_Admin).all()
            list_of_players = session.query(DB_Player).all()
            list_of_players_name = session.query(DB_PlayerNames).all()
            list_of_players_data = session.query(DB_PlayerData).all()

            # 修改查询条件，使用 or_ 函数筛选包含 '_3' 或 '_4' 的记录
            list_of_will_match_of_server_3_4 = session.query(DB_WillMatchs).filter(
                or_(
                    DB_WillMatchs.server_name.contains('_3'),
                    DB_WillMatchs.server_name.contains('_4')
                )
            ).all()

            return {
                "admins": [serialize(admin) for admin in list_of_admin],
                "players": [serialize(player) for player in list_of_players],
                "player_datas": [serialize(player_data) for player_data in list_of_players_data],
                "players_names": [serialize(player_name) for player_name in list_of_players_name],
                "will_matchs": [serialize(will_match) for will_match in list_of_will_match_of_server_3_4]
            }
        
    @classmethod
    def get_match_sync(cls):
        with get_session() as session:
            list_of_will_match_of_server_3_4 = session.query(DB_WillMatchs).filter(
                or_(
                    DB_WillMatchs.server_name.contains('_3'),
                    DB_WillMatchs.server_name.contains('_4')
                )
            ).all()

            return {
                "will_matchs": [serialize(will_match) for will_match in list_of_will_match_of_server_3_4],
            }


if __name__ == '__main__':
    t = DataSyncService.get_sync()
    admins = t.get('admins')
    for i in admins:
        k = safe_deserialize(DB_Admin, i)
        print(k.kookId)
