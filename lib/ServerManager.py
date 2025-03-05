import json
import os.path
import subprocess
import time

import win32con
import win32gui

from lib.LogHelper import display, LogHelper
from lib.ServerGameConfig import GameConfig


class ServerManager:
    @staticmethod
    def RestartBLMMServer(server_index: int = 1):
        for hwnd, title in get_all_windows():
            # print(f'句柄: {hwnd}, 标题: {title}')
            if 'Mount and Blade II Bannerlord Dedicated Server Console' in title:
                close_window(hwnd)
                time.sleep(5.0)
        open_bat(server_index)
        display('重启服务器!')
        # 获取所有顶层窗口句柄和标题

    @staticmethod
    def GenerateConfigFile(config: GameConfig):
        with open(os.path.join(os.getcwd(), 'x.json'), 'r') as f:
            LogHelper.log_star_start()
            z = f.read()
            if len(z) == 0:
                return False
            opx = json.loads(z)
            if not isinstance(opx, dict):
                return False

            server_path = opx.get('SERVER_PATH', '')
            LogHelper.log(f"取得BA服务器路径{server_path}")
            if len(server_path) == 0 or not os.path.exists(server_path):
                LogHelper.log(f"路径异常，退出{server_path}")
                return False

        from lib.ServerGamePathManager import ServerGamePathManager
        file_confit_path = os.path.join(ServerGamePathManager.get_native_path_ex(server_path), 'blmmbot.txt')
        with open(file_confit_path, 'w', encoding='utf8') as f:
            f.write(config.to_str())
        LogHelper.log_star_start()


def open_bat(server_index: int = 1):
    server_desktop = r'C:\Users\Administrator\Desktop'
    bat_name = f'启动BLMM{server_index}.bat'
    bat_path = os.path.join(server_desktop, bat_name)
    subprocess.run(['cmd.exe', '/c', bat_path])


# 关闭窗口函数
def close_window(hwnd):
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)


def foreach_window(hwnd, windows):
    # 获取窗口标题
    title = win32gui.GetWindowText(hwnd)
    # 添加窗口信息到列表
    windows.append((hwnd, title))


def get_all_windows():
    windows = []
    win32gui.EnumWindows(lambda hwnd, param: foreach_window(hwnd, windows), None)
    return windows
