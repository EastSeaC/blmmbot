class ServerGamePathManager:
    GAME_MOD_PATH = ''
    Modules = 'Modules'
    Native = 'Native'

    def get_native_path(self):
        return f"{self.GAME_MOD_PATH}/{self.Modules}/{self.Native}/"

    @staticmethod
    def get_native_path_ex(p: str):
        return f"{p}/{ServerGamePathManager.Modules}/{ServerGamePathManager.Native}/"


if __name__ == '__main__':
    z = ServerGamePathManager.get_native_path_ex('123')
    print(z)
