import json
import random

from init_db import get_session
from tables import DB_Player, DB_PlayerData
from tables.Admin import DB_Admin

from sqlalchemy.orm import class_mapper

from tables.PlayerNames import DB_PlayerNames


class PlayerDataItemForRickyy:
    playerId = ''
    firstTroop = ''
    secondTroop = ''

    def to_dict(self):
        return {
            'firstTroop': self.firstTroop,
            'secondTroop': self.secondTroop,
            'playerId': self.playerId,
        }


class MatchService:
    @classmethod
    def get_random_12(cls):
        with get_session() as session:
            data = []
            x = session.query(DB_Player).all()
            selected_items = random.sample(x, 12)
            for i in selected_items:
                print(i)
                player: DB_Player = i
                item = PlayerDataItemForRickyy()
                item.firstTroop = player.first_troop
                item.secondTroop = player.second_troop
                item.playerId = player.playerId
                data.append(item.to_dict())

            return data


if __name__ == '__main__':
    t = MatchService.get_random_12()
    print(json.dumps(t))
