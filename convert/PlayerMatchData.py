class TPlayerMatchData:
    def __init__(self, data: dict):
        self.player_id = data.get("player_id", "invalid")
        self.player_name = data.get("player_name", "[invalid]")

        self.kill = data.get("KillNum1", 0)
        self.death = data.get("death", 0)
        self.assist = data.get("assist", 0)

        self.match = 1
        self.win = data.get("win", 0)
        self.lose = data.get("Lose1", 0)
        self.draw = data.get("Draw1", 0)
        self.Infantry = data.get("Infantry", 0)
        self.Cavalry = data.get("Cavalry", 0)
        self.Archer = data.get("Archer", 0)

        self.win_rounds = data.get("Win_rounds", 0)
        self.lose_rounds = data.get("Lose_rounds", 0)
        self.draw_rounds = data.get("Draw_rounds", 0)
        self.total_rounds = data.get("Total_rounds", 0)

        self.damage = data.get("damage", 0)
        self.team_damage: int = data.get("team_damage", 0)
        self.tk_times: int = data.get("tk_times", 0)

        self.horse_damage = data.get("horse_damage", 0)
        self.horse_tk = data.get("TKHorse1", 0)

    @property
    def GetHeaders(self):
        return [
            "player_id",
            "player_name",
            "kill",
            "death",
            "assist",
            "match",
            "win",
            "lose",
            "draw",
            "Infantry",
            "Cavalry",
            "Archer",
            "win_rounds",
            "lose_rounds",
            "draw_rounds",
            "total_rounds",
            "damage",
            "team_damage",
            "tk_times",
            "horse_damage",
            "horse_tk"
        ]

    @property
    def get_data_list(self):
        return [
            self.player_id,
            self.player_name,
            self.kill,
            self.death,
            self.assist,
            self.match,
            self.win,
            self.lose,
            self.draw,
            self.Infantry,
            self.Cavalry,
            self.Archer,
            self.win_rounds,
            self.lose_rounds,
            self.draw_rounds,
            self.total_rounds,
            self.damage,
            self.team_damage,
            self.tk_times,
            self.horse_damage,
            self.horse_tk
        ]
