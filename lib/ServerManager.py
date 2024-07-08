import win32gui, win32ui, win32con, win32api


class ServerManager:
    @staticmethod
    def RestartBLMMServer():
        for hwnd, title in get_all_windows():
            print(f'句柄: {hwnd}, 标题: {title}')
        # 获取所有顶层窗口句柄和标题


def foreach_window(hwnd, windows):
    # 获取窗口标题
    title = win32gui.GetWindowText(hwnd)
    # 添加窗口信息到列表
    windows.append((hwnd, title))


def get_all_windows():
    windows = []
    win32gui.EnumWindows(lambda hwnd, param: foreach_window(hwnd, windows), None)
    return windows
