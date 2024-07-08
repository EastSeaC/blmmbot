import os.path
import subprocess
import time

import win32con
import win32gui

from LogHelper import display


class ServerManager:
    @staticmethod
    def RestartBLMMServer():
        for hwnd, title in get_all_windows():
            # print(f'句柄: {hwnd}, 标题: {title}')
            if 'Mount and Blade II Bannerlord Dedicated Server Console' in title:
                close_window(hwnd)
                time.sleep(5.0)
                open_bat()
                display('重启服务器!')
        # 获取所有顶层窗口句柄和标题


def open_bat():
    server_desktop = r'C:\Users\Administrator\Desktop'
    bat_name = '启动BLMM1.bat'
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
