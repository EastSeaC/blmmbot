import json
from datetime import datetime

from init_db import get_session
from lib.log.LoggerHelper import logger
from services.DataSyncService import serialize
from tables import DB_Player, DB_PlayerData, DB_Admin, DB_Ban, DB_WillMatchs, DB_PlayerMedal, DB_MedalPool, \
    DB_KookChannelGroup, DB_Matchs, DB_ScoreLimit


def load_backup(backup_file_path):
    pass


def backup(backup_file_path=None):
    if backup_file_path is None:
        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_file_path = f"backup_{current_time}.json"

    session = get_session()
    all_models = [DB_Player,
                  DB_PlayerData,
                  DB_Admin,
                  DB_Ban,
                  DB_WillMatchs,
                  DB_PlayerMedal,
                  DB_MedalPool,
                  DB_KookChannelGroup,
                  DB_Matchs,
                  DB_ScoreLimit,
                  ]
    backup_data = {}

    try:
        for model in all_models:
            try:
                table_name = model.__tablename__
                records = session.query(model).all()
                serialized_records = []

                for record in records:
                    serialized_records.append(serialize(record))

                backup_data[table_name] = serialized_records
            except Exception as e:
                logger.exception('异常发生')
                print(f"跳过未映射的类 {model.__name__}: {e}")

        with open(backup_file_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=4, default=str)

        print(f"数据库备份成功，备份文件路径: {backup_file_path}")
    except Exception as e:
        print(f"数据库备份失败: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    backup()
