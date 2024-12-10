from config import LOSE_PENALTY_SCORE, WIN_REWARD_SCORE
from wcwidth import wcwidth


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

        self.__old_score = 0
        self.new_score = 0
        self.is_lose = False

    def set_old_score(self, score: int):
        self.__old_score = score

    def get_old_score(self):
        return self.__old_score

    def set_new_score(self, score: int):
        self.new_score = score

    def set_is_lose(self, lose: bool):
        self.is_lose = lose

    def truncate_name(self):
        s = self.player_name
        # 如果字符串的长度大于10，截取前8个字符并添加两个点
        if len(s) > 10:
            return s[:9] + '...'
        return s

    def truncate_by_width(self):
        """
        根据字符的显示宽度截取字符串。

        :param s: 输入的字符串
        :param max_width: 最大显示宽度
        :return: 截取后的字符串
        """
        max_width = 12

        total_width = 0
        result = []

        for char in self.player_name:
            char_width = wcwidth(char)  # 获取字符的显示宽度
            if total_width + char_width > max_width:
                break  # 一旦总宽度超过最大宽度，停止添加字符
            result.append(char)
            total_width += char_width  # 累加当前字符的显示宽度

        return "".join(result)  # 返回截取后的字符串


    '''
    这个函数不会改变self的值
    '''

    def __add__(self, other):
        if not isinstance(other, TPlayerMatchData):
            return NotImplemented
        if self.player_id != other.player_id:
            return ValueError
        new_obj = TPlayerMatchData({})

        new_obj.player_id = self.player_id
        new_obj.player_name = self.player_name

        new_obj.kill = self.kill + other.kill
        new_obj.death = self.death + other.death
        new_obj.assist = self.assist + other.assist
        new_obj.match = self.match + other.match
        new_obj.win = self.win + other.win
        new_obj.lose = self.lose + other.lose
        new_obj.draw = self.draw + other.draw
        new_obj.Infantry = self.Infantry + other.Infantry
        new_obj.Cavalry = self.Cavalry + other.Cavalry
        new_obj.Archer = self.Archer + other.Archer
        new_obj.win_rounds = self.win_rounds + other.win_rounds
        new_obj.lose_rounds = self.lose_rounds + other.lose_rounds
        new_obj.draw_rounds = self.draw_rounds + other.draw_rounds
        new_obj.total_rounds = self.total_rounds + other.total_rounds
        new_obj.damage = self.damage + other.damage
        new_obj.team_damage = self.team_damage + other.team_damage
        new_obj.tk_times = self.tk_times + other.tk_times
        new_obj.horse_damage = self.horse_damage + other.horse_damage
        new_obj.horse_tk = self.horse_tk + other.horse_tk
        return new_obj

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

    @property
    def get_kill_info(self):
        return f'''战场表现:
Kills:{self.kill}
Deaths:{self.death}
KDA:{(self.kill + self.assist) / max(self.death, 1)}
KD: {self.kill / max(self.death, 1)}
伤害/TK: {self.damage}/{self.team_damage}
        '''

    @property
    def get_kill_info_2(self):
        return f'''{self.kill}/{self.assist}/{self.death}'''

    @property
    def get_game_info(self):
        return f'''**游戏**
对局数:{self.match}
胜场:{self.win}
败场:{self.lose}
平局:{self.draw}
胜/败:{self.win / max(self.lose, 1)}
MVPs:{0}'''

    @property
    def get_score_info(self):
        return f"得分: (font){LOSE_PENALTY_SCORE}(font)['warning'] 最终分:(font){self.get_old_score()} -> {self.new_score}(font)[{'purple'}]" if self.is_lose else f"得分: (font){WIN_REWARD_SCORE}(font)[{'success'}] 最终分:(font){self.get_old_score()} -> {self.new_score}(font)[{'success'}]"

    @property
    def get_score_info_2(self):
        return f"(font){self.get_old_score()} -> {self.new_score}(font)[{'purple'}]" if self.is_lose else f"(font){self.get_old_score()} -> {self.new_score}(font)[{'success'}]"
