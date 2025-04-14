class AdminButtonValue:
    Show_OrganizationPlayers = 'Show_OrganizationPlayers'
    Show_Server_State = 'show_server_state'
    Show_Last_Match = 'show_last_match'
    Show_Last_5_Matches = 'show_last_5_matches'
    Refresh_All_VerifyCode = 'Refresh_All_VerifyCode'
    Refresh_Server_NotForce = 'Refresh_Server_NotForce'
    Refresh_Server_Force = 'Refresh_Server_Force'
    Refresh_Server6_Force = 'Refresh_Server6_Force'
    Reset_Server_ChannelSet = 'Reset_Server_ChannelSet'

    Restart_Server_1 = 'Refresh_Server_Force_1'
    Restart_Server_2 = 'Refresh_Server_Force_2'
    Restart_Server_3 = 'Refresh_Server_Force_3'

    @classmethod
    def is_admin_command(cls, a: str):
        # Get all class attributes (excluding methods and special vars)
        admin_values = {
            value for key, value in vars(cls).items()
            if not key.startswith('__') and not callable(value)
        }
        return a in admin_values


class PlayerButtonValue:
    ShowServerState = 'ShowServerState'
    player_wonder_server_state = 'player_wonder_server_state'
    player_score = 'player_score'
    player_score_list = 'player_score_list'


class ESActionType:
    Admin_Cancel_Match = 'admin-cancel-match'
