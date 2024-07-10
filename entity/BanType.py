class BanType:
    ForbiddenJoinChannel = 'ForbiddenJoinChannel'
    ForbiddenJoinServer = 'ForbiddenJoinServer'

    @staticmethod
    def get_type_from_int(a: int):
        if a is 1:
            return BanType.ForbiddenJoinServer
        else:
            return BanType.ForbiddenJoinChannel
