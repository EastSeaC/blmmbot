import io
import json
import os.path
import platform
import re
import signal
import subprocess
import time
from datetime import datetime

import win32con
import win32gui

from entity.ServerEnum import ServerEnum
from lib.LogHelper import display, LogHelper
from lib.ServerGameConfig import GameConfig


class ServerManager:
    """
    这个class 用于管理 BLMM系统的 token文件等等
    """
    toke_file_path = r'C:\Users\Administrator\Documents\Mount and Blade II Bannerlord\Tokens\DedicatedCustomServerAuthToken.txt'

    server_1_handle = None
    server_1_pid = None

    @staticmethod
    def check_token_file():
        toke_file_path = ServerManager.toke_file_path
        result = '未知'
        if not os.path.exists(toke_file_path):
            result = 'token文件不存在'
        else:
            # 获取文件修改时间（时间戳）
            mod_time = os.path.getmtime(toke_file_path)
            # 转换为 datetime 对象
            file_mod_time = datetime.fromtimestamp(mod_time)
            # 将时间戳转换为可读格式
            readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))
            result = f'token文件存在，最后修改时间: {readable_time}'
            # 获取当前时间
            current_time = datetime.now()
            # 计算时间差
            time_diff = current_time - file_mod_time
            # 提取天数
            days_diff = time_diff.days
            result = f'token文件存在，最后修改时间: {readable_time}，距今 {days_diff} 天'

            if days_diff >= 60:
                result += '【快去重新生成一份token文件！】'
        return result

    @staticmethod
    def RestartBLMMServer(server_index: int = 1):
        return False
        # for hwnd, title in get_all_windows():
        #     # print(f'句柄: {hwnd}, 标题: {title}')
        #     if 'Mount and Blade II Bannerlord Dedicated Server Console' in title:
        #         close_window(hwnd)
        #         time.sleep(5.0)
        # open_bat(server_index)
        # display('重启服务器!')
        # 获取所有顶层窗口句柄和标题

    @staticmethod
    def RestartBLMMServerEx(server_index: ServerEnum):
        port = ServerManager.GetTargetPort(server_index)
        pid = find_pid_by_port_windows(port)
        if pid is not None:
            if kill_process_by_pid(pid):
                LogHelper.log(f'关闭服务器')
                time.sleep(1)
        generateBatFile(server_index)
        time.sleep(1)
        open_bat(server_index.value[0])

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

    @classmethod
    def CheckConfitTextFile(cls, use_server_x: ServerEnum):
        px = f'C:\\Users\\Administrator\\Desktop\\server files license\\Modules\\Native\\blmm_{use_server_x.value}_x.txt'
        return px
        pass

    @classmethod
    def GetTargetPort(cls, use_server_x: ServerEnum):
        print(use_server_x.value)
        return 7100 - 1 + use_server_x.value[0]


def generateBatFile(use_server_x: ServerEnum):
    path_a = f'C:\\Users\\Administrator\\Desktop\\启动blmm_{use_server_x.value[0]}_x.bat'
    if not os.path.exists(path_a):
        with open(path_a, 'w') as f:
            text_a = '\n'.join([
                'cd /d "C:\\Users\\Administrator\\Desktop\\server files license\\bin\\Win64_Shipping_Server"',
                f'start DedicatedCustomServer.Starter.exe /no_watchdog /dedicatedcustomserverconfigfile blmm_{use_server_x.value[0]}_x.txt /port {ServerManager.GetTargetPort(use_server_x)} /LogOutputPath "C:\\Users\\Administrator\\Documents\\log" /multiplayer _MODULES_*Native*Multiplayer*BLMMX*_MODULES_'
            ])
            f.write(text_a)


def open_bat(server_index: int = 1):
    server_desktop = r'C:\Users\Administrator\Desktop'
    bat_name = f'启动BLMM{server_index}_x.bat'
    bat_path = os.path.join(server_desktop, bat_name)

    print('启动！' + bat_path)
    subprocess.run(['cmd.exe', '/c', bat_path])


def find_pid_by_port_windows(port):
    # 执行 netstat 命令获取端口和 PID
    result = subprocess.run(
        ["netstat", "-ano"],
        capture_output=True,
        text=True,
        shell=True
    )

    # 用正则匹配端口对应的行
    pattern = re.compile(f":{port}\\s.*LISTENING\\s+(\\d+)")
    match = pattern.search(result.stdout)

    if match:
        pid = match.group(1)
        print(f"端口 {port} 对应的 PID: {pid}")
        return int(pid)
    else:
        print(f"未找到端口 {port} 对应的进程")
        return None


def kill_process_by_pid(pid):
    system = platform.system().lower()

    try:
        if system == "windows":
            # Windows 使用 `signal.CTRL_C_EVENT` 或强制终止
            os.kill(pid, signal.SIGTERM)  # 优雅终止
            # os.kill(pid, signal.SIGKILL)  # 强制终止（类似 taskkill /F）
        else:
            # Linux/macOS 使用 SIGTERM（优雅终止）或 SIGKILL（强制终止）
            os.kill(pid, signal.SIGTERM)  # 默认优雅终止
            # os.kill(pid, signal.SIGKILL)  # 强制终止

        print(f"已发送终止信号到 PID: {pid}")
        return True
    except ProcessLookupError:
        print(f"进程 {pid} 不存在")
        return False
    except PermissionError:
        print(f"无权限终止进程 {pid}（可能需要管理员权限）")
        return False


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
