class WillMatchType:
    Test11 = 'Test11'
    Match33 = 'Match33'
    Match66 = 'Match66'
    Match88 = 'Match88'

    @classmethod
    def get_match_type_with_player_num(cls, a: int):
        if a == 1:
            return WillMatchType.Test11
        elif a == 3:
            return WillMatchType.Match33
        elif a == 6:
            return WillMatchType.Match66
        elif a == 8:
            return WillMatchType.Match88
