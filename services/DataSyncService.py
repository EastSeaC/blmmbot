from init_db import get_session
from tables import Player, DB_PlayerData
from tables.Admin import DB_Admin

from sqlalchemy.orm import class_mapper

from tables.PlayerNames import DB_PlayerNames


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
            list_of_players = session.query(Player).all()
            list_of_players_name = session.query(DB_PlayerNames).all()
            list_of_players_data = session.query(DB_PlayerData).all()

            return {
                "admins": [serialize(admin) for admin in list_of_admin],
                "players": [serialize(admin) for admin in list_of_players],
                "player_datas": [serialize(admin) for admin in list_of_players_data],
                "players_names": [serialize(admin) for admin in list_of_players_name],
            }


if __name__ == '__main__':
    t = DataSyncService.get_sync()
    admins = t.get('admins')
    for i in admins:
        k = safe_deserialize(DB_Admin, i)
        print(k.kookId)
