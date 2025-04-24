from khl import PublicVoiceChannel, PublicTextChannel

from entity.ServerEnum import ServerEnum
from kook.Enum.KookTextColorEnum import TextColorEnum
from lib.LogHelper import LogHelper


class ChannelManager:
    # 服务器
    sever = '2784764957685998'
    # 公告区
    announcement = '7368706706716074'
    # 集结频道ID
    old_wait_channel = '3137719365146347'
    # 休息室
    sleep_room_channel = '2602141163900435'
    # 比赛分组
    match_group = '3182448324425808'
    # 候选频道语音
    match_wait_channel = '6713919713207768'
    match_attack_channel = '5436769046749546'
    match_defend_channel = '8246783800929740'

    match_set_channel = '9152989485766507'  # 淘汰休息室
    match_high_score_match_channel = '8860007123246981'  # 高分频道
    # 警告频道
    error_channel = '3489054506196442'
    es_user_id = '482714005'

    # 通用 人类提示频道
    common_channel = '3137719365146347'
    command_channel = '3971225977704461'
    manager_user_id = ['482714005',
                       '404770518',  # 大C
                       '1439484517',  # 小明？
                       '3743625354',  # 海棠
                       ]

    organization_user_ids = [

    ]

    @staticmethod
    def is_es(kook_id: str):
        if kook_id == ChannelManager.es_user_id:
            return True
        else:
            return False

    @staticmethod
    def is_admin(kook_id: str):
        if kook_id in ChannelManager.manager_user_id:
            return True
        pass

    @staticmethod
    def is_organization_user(kook_id: str):
        return ChannelManager.is_admin(kook_id) or kook_id in ChannelManager.organization_user_ids

    @staticmethod
    def get_command_channel_id(guild_id: str):
        if guild_id == '9019084812125033':
            return "1451138349000890"
        elif guild_id == '2784764957685998':
            return "3971225977704461"

    @staticmethod
    def get_color_text(a: str, b: TextColorEnum):
        return f'**(font){a}(font)[{b.value}]**'

    @staticmethod
    def get_emoji_id():
        return "ScZtMJaGPk0b40b4"

    __base_emoji = "(emj){}(emj)[{}]"

    emoji_farmer = __base_emoji.format('农民', '2784764957685998/ScZtMJaGPk0b40b4')
    emoji_joker = __base_emoji.format('小丑', '2784764957685998/3xeNeLlxjz0b40b4')

    emoji_infantry = __base_emoji.format('步兵', '9019084812125033/WN0jvQAtEY00o01r')
    emoji_archer = __base_emoji.format('射手', '9019084812125033/usVMZodUDl01700u')
    emoji_calvary = __base_emoji.format('骑士', '9019084812125033/Miw85Tj2UO01900u')

    image_joker = 'https://img.kookapp.cn/assets/2024-12/30/amsrdVMzVI0b40b4.png'
    image_farmer = 'https://img.kookapp.cn/assets/2024-12/30/jxTLdruutF0b40b4.png'
    image_big_knight = 'https://img.kookapp.cn/assets/2024-12/30/4Nnslswg3g0b40b4.png'
    image_big_knight_2 = 'https://img.kookapp.cn/assets/2024-12/30/U0bx0f56nw01s01s.png'
    image_follower = 'https://img.kookapp.cn/assets/2024-12/30/aXfKXOO9Q90b40b4.png'
    image_guard = 'https://img.kookapp.cn/assets/2024-12/30/V5Nx6soV1J0b40b4.png'
    image_knight = 'https://img.kookapp.cn/assets/2025-04/21/WWHWntc8Oh0e80e8.png'

    image_lord = 'https://img.kookapp.cn/assets/2024-12/30/ZUAQnICKXb0e80e8.png'
    image_duke = 'https://img.kookapp.cn/assets/2024-12/30/XlFk0gAFp201s01s.png'
    image_prince = 'https://img.kookapp.cn/assets/2024-12/30/um0wBP2AxU01s01s.png'
    image_king = 'https://img.kookapp.cn/assets/2024-12/30/nD4S34VrVb01s01s.png'
    image_empire = 'https://img.kookapp.cn/assets/2024-12/30/ryDINs0i7k01s01s.png'

    image_type_archer = 'https://img.kookapp.cn/assets/2024-12/30/jCU7Ajes1Q01700u.png'
    image_type_knight = 'https://img.kookapp.cn/assets/2024-12/30/3N44Nt0Cdl01900u.png'
    image_type_infantry = 'https://img.kookapp.cn/assets/2024-12/31/lWP0puaPuH074074.png'

    @staticmethod
    def get_troop_emoji(a: int):
        if a == 0:
            return ChannelManager.emoji_infantry
        elif a == 1:
            return ChannelManager.emoji_calvary
        elif a == 2:
            return ChannelManager.emoji_archer
        return ChannelManager.emoji_infantry

    @staticmethod
    def is_common_user(kook_id: str):
        return kook_id not in ChannelManager.manager_user_id

    @classmethod
    def get_server_name(cls, index: int = 0):
        return f'BLMM_{index}'

    @classmethod
    def get_at(cls, kook_id: str):
        return f'(met){kook_id}(met)'


class OldGuildChannel:
    # 服务器
    sever = '9019084812125033'
    # 公告区
    announcement = '7368706706716074'
    # 集结频道ID
    old_wait_channel = '3137719365146347'
    # 休息室
    sleep_room_channel = '2602141163900435'
    # 比赛分组
    match_group = '8867447588765353'
    # 候选频道语音
    match_wait_channel = '9263713909740224'
    # 1队频道
    match_attack_channel = '5436769046749546'
    match_defend_channel = '8246783800929740'

    match_set_channel = '6713919713207768'  # 淘汰休息室
    # 警告频道
    error_channel = '3489054506196442'
    es_user_id = '482714005'

    # 通用 人类提示频道
    common_channel = '3137719365146347'
    command_channel = '1451138349000890'

    manager_user_id = ['482714005', '404770518', '1439484517', '3743625354', '2806603494']

    match_attack_channel_2 = '5889652844944800'
    match_defend_channel_2 = '8324383899171681'

    match_attack_channel_3 = '4653727651132216'
    match_defend_channel_3 = '7136051179773177'

    match_attack_channel_4 = '6549179321865306'
    match_defend_channel_4 = '7270117468200787'

    command_select_channel = '4437897819137837'  # 选人指令频道
    match_select_channel = '2645329202100415'  # 选人频道

    @classmethod
    def get_match_channels(cls, server_enum: ServerEnum):
        """Returns (attack_channel, defend_channel) based on the server enum."""
        if server_enum == ServerEnum.Server_1:
            return cls.match_attack_channel, cls.match_defend_channel
        elif server_enum == ServerEnum.Server_2:
            return cls.match_attack_channel_2, cls.match_defend_channel_2
        elif server_enum == ServerEnum.Server_3:
            return cls.match_attack_channel_3, cls.match_defend_channel_3
        elif server_enum == ServerEnum.Server_4:
            return cls.match_attack_channel_4, cls.match_defend_channel_4

        return cls.match_wait_channel, cls.match_wait_channel

    @classmethod
    def get_at(cls, kook_id: str):
        return f'(met){kook_id}(met)'

    @classmethod
    def get_server_name(cls, index: int = 0):
        return f'BLMM_{index}'

    @classmethod
    def get_category_list_name(cls):
        return [f'BLMM_{i}' for i in range(1, 4 + 1)]

    command_channel_name = '指令频道'
    channel_a_team = 'A队'
    channel_b_team = 'B队'
    channel_wait_room = '休息室'
    channel_eliminate_room = '淘汰休息室'


def get_troop_type_image(a: int):
    if a is None or a < 2:
        return ChannelManager.image_type_infantry
    elif a == 2:
        return ChannelManager.image_type_knight
    elif a == 3:
        return ChannelManager.image_type_archer


def kim(rank_name: str):
    if rank_name == '小丑' or rank_name == 'joker':
        return ChannelManager.image_joker
    elif rank_name == '农民' or rank_name == 'farmer':
        return ChannelManager.image_farmer

    elif rank_name == '侍从':
        return ChannelManager.image_follower
    elif rank_name == '守卫':
        return ChannelManager.image_guard
    elif rank_name == '骑士':
        return ChannelManager.image_knight
    elif rank_name == '大骑士' or rank_name == 'bigknight':
        return ChannelManager.image_big_knight_2
    elif rank_name == '领主':
        return ChannelManager.image_lord
    elif rank_name == '公爵':
        return ChannelManager.image_duke
    elif rank_name == '王子':
        return ChannelManager.image_prince
    elif rank_name == '国王':
        return ChannelManager.image_king
    elif rank_name == '皇帝':
        return ChannelManager.image_empire


class EsChannels:
    _instance = None

    def __init__(self):
        self.wait_channel = ''
        self.match_attack_channel = ''
        self.match_defend_channel = ''
        self.command_channel = None

        self.ready: bool = False

    async def Initial(self, bot1):
        self.wait_channel: PublicVoiceChannel = await bot1.client.fetch_public_channel(
            OldGuildChannel.match_wait_channel)
        self.match_attack_channel: PublicVoiceChannel = await bot1.client.fetch_public_channel(
            OldGuildChannel.match_attack_channel)
        self.match_defend_channel: PublicVoiceChannel = await  bot1.client.fetch_public_channel(
            OldGuildChannel.match_defend_channel)
        self.command_channel: PublicTextChannel = await  bot1.client.fetch_public_channel(
            OldGuildChannel.command_channel)

        self.ready = True
        EsChannels._instance = self
        LogHelper.log("初始化频道成功")

    @classmethod
    def instance(cls):
        return cls._instance
