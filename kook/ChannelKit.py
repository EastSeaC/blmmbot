from khl import PublicVoiceChannel, PublicTextChannel

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
    match_wait_channel = '7483461728419145'
    match_attack_channel = '4855555618242776'
    match_defend_channel = '7704290253382922'

    match_set_channel = '9152989485766507'  # 淘汰休息室
    # 警告频道
    error_channel = '3489054506196442'
    es_user_id = '482714005'

    # 通用 人类提示频道
    common_channel = '3137719365146347'
    command_channel = '3971225977704461'
    manager_user_id = ['482714005', '404770518', '1439484517', '3743625354', '2806603494']

    @staticmethod
    def get_command_channel_id(guild_id: str):
        if guild_id == '9019084812125033':
            return "1451138349000890"
        elif guild_id == '2784764957685998':
            return "3971225977704461"

    @staticmethod
    def get_emoji_id():
        return "ScZtMJaGPk0b40b4"

    __base_emoji = "(emj){{}}(emj)[{}]"

    emoji_farmer = __base_emoji.format('农民', 'ScZtMJaGPk0b40b4')
    emoji_joker = __base_emoji.format('小丑', '3xeNeLlxjz0b40b4')

    @staticmethod
    def is_common_user(kook_id: str):
        return kook_id not in ChannelManager.manager_user_id


class EsChannels:
    def __init__(self):
        self.wait_channel = ''
        self.match_attack_channel = ''
        self.match_defend_channel = ''

        self.ready: bool = False

    async def Initial(self, bot1):
        self.wait_channel: PublicVoiceChannel = await bot1.client.fetch_public_channel(
            ChannelManager.match_wait_channel)
        self.match_attack_channel: PublicVoiceChannel = await bot1.client.fetch_public_channel(
            ChannelManager.match_attack_channel)
        self.match_defend_channel: PublicVoiceChannel = await  bot1.client.fetch_public_channel(
            ChannelManager.match_defend_channel)
        self.command_channel: PublicTextChannel = await  bot1.client.fetch_public_channel(
            ChannelManager.command_channel)
        self.ready = True
        LogHelper.log("初始化频道成功")
