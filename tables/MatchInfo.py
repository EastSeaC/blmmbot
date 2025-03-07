from sqlalchemy import *

from convert.PlayerMatchData import TPlayerMatchData
from lib.BannerlordTeam import BannerlordTeam
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

    tag = Column(Text, nullable=True, default='Test')

    raw = Column(JSON, nullable=False, default='{}')
    player_data = Column(JSON, nullable=False, default='')
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

    def get_player_team(self, player_id: str):
        if player_id in self.left_players:
            return BannerlordTeam.FirstTeam
        elif player_id in self.right_players:
            return BannerlordTeam.SecondTeam
        else:
            return BannerlordTeam.Invalid
        pass

    # def get_enemy_team_spawn_times(self, player_id: str):
    #     PlayerTeam = self.get_player_team(player_id)
    #     if PlayerTeam == BannerlordTeam.FirstTeam:
    #         return self.right_players_spawn_times
    #     elif PlayerTeam == BannerlordTeam.SecondTeam:
    #         return self.left_players_spawn_times
    #     else:
    #         raise ValueError
    #     pass

    @property
    def get_total_data(self):
        match_sum_data = MatchSumData()
        match_sum_data.total_round = int(self.tag.RoundCount)
        # print('123X-tesrt')
        # print(self.player_data.values())
        all_player_data = [TPlayerMatchData(i) for i in self.player_data.values()]

        match_sum_data.first_team_total_spawn_times = sum(
            [i.spawn_times for i in all_player_data if i.player_id in self.left_players])
        print(match_sum_data.first_team_total_spawn_times)
        match_sum_data.first_team_total_death_times = sum(
            [i.death for i in all_player_data if i.player_id in self.left_players]
        )
        match_sum_data.first_team_total_assist_times = sum(
            [i.assist for i in all_player_data if i.player_id in self.left_players]
        )

        match_sum_data.second_team_total_spawn_times = sum(
            [i.spawn_times for i in all_player_data if i.player_id in self.right_players])
        match_sum_data.second_team_total_death_times = sum(
            [i.death for i in all_player_data if i.player_id in self.right_players]
        )
        match_sum_data.second_team_total_assist_times = sum(
            [i.assist for i in all_player_data if i.player_id in self.right_players]
        )

        return match_sum_data


class MatchSumData:
    def __init__(self):
        self.first_team_total_spawn_times = 0
        self.second_team_total_spawn_times = 0

        self.first_team_total_death_times = 0
        self.second_team_total_death_times = 0

        self.first_team_total_assist_times = 0
        self.second_team_total_assist_times = 0

        self.total_round = 0
