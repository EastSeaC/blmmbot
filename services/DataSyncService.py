from init_db import get_session
from tables.Admin import DB_Admin

from sqlalchemy.orm import class_mapper


def serialize(model):
    columns = [c.key for c in class_mapper(model.__class__).columns]
    return dict((c, getattr(model, c)) for c in columns)


class DataSyncService:
    @classmethod
    def get_admin(cls):
        with get_session() as session:
            list_of_admin = session.query(DB_Admin).all()
            return [serialize(admin) for admin in list_of_admin]
