from datetime import datetime


def get_time_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def display(s):
    LogHelper.log(s)


start_str = "*" * 75


class LogHelper:
    __open_log = True

    @staticmethod
    def log_star_start(s='分界线'):
        print(start_str + f"[{get_time_str()}]:{s}{start_str}")

    @staticmethod
    def log(s):
        if LogHelper.__open_log:
            print(f"[{get_time_str()}]:{s}")
