from datetime import datetime


def get_time_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class LogHelper:
    __open_log = True

    @staticmethod
    def log(s):
        if LogHelper.__open_log:
            print(f"[{get_time_str()}]:{s}")
