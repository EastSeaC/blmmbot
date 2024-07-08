import win32gui, win32ui, win32con, win32api


class ServerManager:
    @staticmethod
    def RestartBLMMServer():

        #   GetDesktopWindow 获得代表整个屏幕的一个窗口（桌面窗口）句柄
        hd = win32gui.GetDesktopWindow()

        # 获取所有子窗口
        hwndChildList = []
        #   EnumChildWindows 为指定的父窗口枚举子窗口
        win32gui.EnumChildWindows(hd, lambda hwnd, param: param.append(hwnd), hwndChildList)
        print(hwndChildList)
        for hwnd in hwndChildList:
            #   GetWindowText 取得一个窗体的标题（caption）文字，或者一个控件的内容
            print("句柄：", hwnd, "标题：", win32gui.GetWindowText(hwnd))