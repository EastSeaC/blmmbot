import random

from lib.LogHelper import LogHelper


def get_random_faction_2():
    z = ['sturgia', 'vlandia', 'battania', 'empire', 'khuzait', 'aserai']
    # 从列表中随机选择两个元素
    random_selection = random.sample(z, 2)
    return random_selection


class GameConfig:
    def __init__(self,
                 server_name: str,
                 match_id: str,
                 culture_team1: str = 'khuzait',
                 culture_team2: str = 'aserai',
                 map_name: str = '',
                 ):
        self.server_name = f"{server_name}-{match_id}"
        self.game_type = "Skirmish"
        self.admin_password = "btl626"
        self.game_password = "blmm"
        if map_name != '':
            # self.automated_battle_pool = [map_name]
            self.map = map_name
        else:
            self.map = "mp_skirmish_map_007"
        self.culture_team1 = culture_team1
        self.culture_team2 = culture_team2
        self.respawn_period_team1 = 3
        self.respawn_period_team2 = 3
        self.round_preparation_time_limit = 25
        self.max_number_of_players = 64
        self.auto_team_balance_threshold = 0
        self.friendly_fire_damage_melee_friend_percent = 50
        self.friendly_fire_damage_melee_self_percent = 0
        self.friendly_fire_damage_ranged_friend_percent = 50
        self.friendly_fire_damage_ranged_self_percent = 0
        self.min_number_of_players_for_match_start = 2
        self.round_total = 10
        self.map_time_limit = 8
        self.round_time_limit = 420
        self.warmup_time_limit = 60
        self.allow_polls_to_change_maps = True
        self.automated_battle_count = -1
        self.automated_battle_switching_enabled = True

    def shuffle_all(self):
        self.automated_battle_pool = []
        self.map = random.sample(self.automated_battle_pool, k=1)
        self.ramdom_faction()
        LogHelper.log('打乱成功')
        pass

    def ramdom_faction(self):
        x, y = get_random_faction_2()
        self.culture_team1 = x
        self.culture_team2 = y

    def start_game_and_mission(self):
        # Placeholder for starting game and mission logic
        print(self)

    def to_str(self):
        return self.__str__()

    def __str__(self):
        self.automated_battle_pool = []
        automated_battle_pool_str = ''.join(
            [f"add_map_to_automated_battle_pool {i}\n" for i in self.automated_battle_pool])

        return (f"ServerName {self.server_name}\n"
                f"GameType {self.game_type}\n"
                f"AdminPassword {self.admin_password}\n"
                f"#GamePassword {self.game_password}\n"
                # f"{automated_battle_pool_str}"
                # f"enable_map_voting\n"
                # f"enable_culture_voting\n"
                f"add_map_to_automated_battle_pool {self.map}\n"
                f"Map {self.map}\n"
                f"CultureTeam1 {self.culture_team1}\n"
                f"CultureTeam2 {self.culture_team2}\n"
                f"RespawnPeriodTeam1 {self.respawn_period_team1}\n"
                f"RespawnPeriodTeam2 {self.respawn_period_team2}\n"
                f"RoundPreparationTimeLimit {self.round_preparation_time_limit}\n"
                f"MaxNumberOfPlayers {self.max_number_of_players}\n"
                f"AutoTeamBalanceThreshold {0}\n"
                f"FriendlyFireDamageMeleeFriendPercent {self.friendly_fire_damage_melee_friend_percent}\n"
                f"FriendlyFireDamageMeleeSelfPercent {self.friendly_fire_damage_melee_self_percent}\n"
                f"FriendlyFireDamageRangedFriendPercent {self.friendly_fire_damage_ranged_friend_percent}\n"
                f"FriendlyFireDamageRangedSelfPercent {self.friendly_fire_damage_ranged_self_percent}\n"
                f"MinNumberOfPlayersForMatchStart {self.min_number_of_players_for_match_start}\n"
                f"SpectatorCameraTypes 6\n"
                f"RoundTotal {self.round_total}\n"
                f"MapTimeLimit {self.map_time_limit}\n"
                f"RoundTimeLimit {self.round_time_limit}\n"
                f"WarmupTimeLimit {self.warmup_time_limit}\n"
                # f"AllowPollsToChangeMaps {self.allow_polls_to_change_maps}\n"
                # f"AutomatedBattleCount {self.automated_battle_count}\n"
                # f"AutomatedBattleSwitchingEnabled {self.automated_battle_switching_enabled}\n"
                f"end_game_after_mission_is_over\n"
                f"enable_automated_battle_switching\n"
                f"start_game_and_mission"
                )


class MapSequence:
    def __init__(self):
        self.maps = [
            # "mp_adimiduel_empire",
            # "mp_adimiduel_vlandia",
            "mp_bnl_fortlieve",
            # "mp_bnl_ghosttown",
            "mp_bnl_lighthouse",
            "mp_bnl_purplehaze",
            "mp_skirmish_map_007",
            "mp_skirmish_map_010",
            "mp_skirmish_map_020",
            "mp_skirmish_map_008_skin",
            "mp_skirmish_map_003_skinc",
            "mp_skirmish_map_002f",
        ]
        self.index = 0

    def get_next_map(self):
        current_map = self.maps[self.index]
        self.index = (self.index + 1) % len(self.maps)
        return current_map


# Example usage
if __name__ == '__main__':
    config = GameConfig(32)
    config.start_game_and_mission()
