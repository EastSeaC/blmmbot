from khl import PublicVoiceChannel, PublicTextChannel

from LogHelper import LogHelper


class ChannelManager:
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
    match_attack_channel = '4829289747409514'
    match_defend_channel = '1565042036823961'

    match_set_channel = '7650865243361968'
    # 警告频道
    error_channel = '3489054506196442'
    es_user_id = '482714005'

    # 通用 人类提示频道
    common_channel = '3137719365146347'
    command_channel = '1451138349000890'
    manager_user_id = ['482714005', '404770518', '1439484517', '3743625354', '2806603494']


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
