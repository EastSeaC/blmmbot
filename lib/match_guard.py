'''
作为护卫，应当记录玩家离开频道次数
'''

from datetime import datetime, timedelta


class MatchGuard:
    def __init__(self) -> None:
        self.leave_times = {}
        self.kick_threshlold = 3
        self.temp_ban = {}
        pass

    def add_player(self, user_id: str):
        self.leave_times[user_id] = 0

    def add_warning_times(self, user_id: str):
        if user_id in self.leave_times:
            times = self.leave_times[user_id]
            times += 1
            self.leave_times[user_id] = times

            if times < self.kick_threshlold:
                return False, times
            else:
                return True, times
        else:
            self.leave_times[user_id] = 1
            return False, 1

    def add_temp_ban(self, user_id: str):
        current_datetime = datetime.now() + timedelta(minutes=30)
        datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.temp_ban[user_id] = datetime_string

    def remove_ban(self):
        current_datetime = datetime.now()
        for key, val in self.temp_ban.items():
            formatted_datetime = datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
            if current_datetime > formatted_datetime:
                self.temp_ban.pop(key)
        pass

    def refresh(self):
        self.__init__()
