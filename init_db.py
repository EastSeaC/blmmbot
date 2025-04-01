from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event

from config import *
from tables import *

global engine
engine = create_engine(f'{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8')
engine.connect()


@event.listens_for(engine, "close")
def receive_close(conn, exception):
    global engine
    engine = create_engine(f'{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8')
    engine.connect()
    print("连接关闭,重新连接")


def get_session():
    try:
        global engine
        Session = sessionmaker(bind=engine)
    except Exception as e:
        engine = create_engine(f'{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8')
        engine.connect()
        Session = sessionmaker(bind=engine)

        pass
    session = Session()
    Base.metadata.create_all(engine)
    return session


def __test_a():
    session = get_session()

    # session.query(Player).filter(Player.playerId)


# engine = sqlalchemy.create_engine(
#         "%s+%s://%s:%s@%s:%d/?charset=utf8" % (DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT))
if __name__ == '__main__':
    engine = create_engine(f'{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8')
    connect = engine.connect()
    Base.metadata.create_all(engine)  # 创建表结构
    # player = Player.query().filter(Player.playerId == '2.0.0.76561199044372880').first()
    # print(player)

    # 创建持久化session 这个对象可以和数据库进行交互
    Session = sessionmaker(bind=engine)
    session = Session()
    #
    # to_add = Player()
    # to_add.playerId = '2.0.0.76561199044372880'
    # to_add.kookId = '6784aaa'
    # session.add(to_add)
    # session.commit()
# tlayer: Player = session.query(Player).filter(Player.playerId == '2.0.0.76561199044372880').first()
# print(tlayer.playerId)
