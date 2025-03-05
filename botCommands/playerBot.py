import json

from khl import Bot, Message, GuildUser, EventTypes, Event
from khl.card import CardMessage, Card, Module, Struct, Element, Types

from botCommands.adminButtonValueImpl import AdminButtonValue
from lib.LogHelper import LogHelper, get_time_str
from config import get_rank_name
from init_db import get_session
from kook.ChannelKit import EsChannels, ChannelManager, kim, get_troop_type_image
from lib.SelectMatchData import SelectPlayerMatchData
from lib.ServerManager import ServerManager
from lib.match_state import PlayerBasicInfo, DivideData, MatchState, MatchConditionEx
from tables import *
from tables.PlayerChangeName import DB_PlayerChangeNames

sqlSession = get_session()
g_channels: EsChannels


def init(bot: Bot, es_channels: EsChannels):
    global g_channels
    g_channels = es_channels

    @bot.command(name='score_list', case_sensitive=False, aliases=['sl'])
    async def world(msg: Message, *args):
        cm = CardMessage()

        sqlSession.commit()
        t = sqlSession.query(Player).order_by(Player.rank.desc()).limit(10).all()
        print(t)
        kill_scoreboard = '**积分榜单**'
        for id, k in enumerate(t):
            player: Player = k
            kill_scoreboard += f"\n{player.kookName}:{player.rank}"

        game_scoreboard = '**对局榜单**'
        t = sqlSession.query(Player).order_by(Player.win.desc()).limit(10).all()
        for id, k in enumerate(t):
            player: Player = k
            game_scoreboard += f"\n{player.kookName}:{player.win}"

        c2 = Card(
            Module.Section(
                Struct.Paragraph(
                    3,
                    Element.Text(kill_scoreboard, type=Types.Text.KMD),
                    Element.Text(game_scoreboard, type=Types.Text.KMD),
                    Element.Text(f"**步/骑/弓弩**\n",
                                 type=Types.Text.KMD),
                )
            )
        )
        cm.append(c2)
        await msg.reply(cm)

    @bot.command(name='reset_score', case_sensitive=False, aliases=['rs'])
    async def reset_score(msg: Message, *args):

        pass

    """
    开启匹配指令
    is_no_move: 1 表示 不移动玩家，仅用作测试
    """

    @bot.command(name='e', case_sensitive=False, aliases=['e'])
    async def es_start_match(msg: Message, is_no_move: int = 0):
        if ChannelManager.is_common_user(msg.author_id):
            await msg.reply('禁止使用es指令')
            return
        try:
            sqlSession.commit()
        except Exception as e:
            await msg.reply('数据库提交异常')
            sqlSession.rollback()

        k = await es_channels.wait_channel.fetch_user_list()
        for i in k:
            z: GuildUser = i
            print(z.__dict__)
            print(convert_timestamp(z.active_time))
        number_of_user = len(k)
        if number_of_user % 2 == 1 or number_of_user == 0:
            await msg.reply(f'人数异常, 当前人数为 {len(k)} , 必须为非0偶数')
            return
        player_list = []

        z = sqlSession.query(Player).filter(Player.kookId.in_([i.id for i in k])).all()
        dict_for_kook_id = {}
        for i in z:
            t: Player = i
            dict_for_kook_id[t.kookId] = t

        # print([i.__dict__ for i in z])
        # print([i.__dict__ for i in dict_for_kook_id.values()])
        try:
            for id, user in enumerate(k):
                t: GuildUser = user
                if t.id not in dict_for_kook_id:
                    await es_channels.command_channel.send(f'(met){t.id}(met) 你没有注册，请先注册')
                    await move_a_to_b_ex(ChannelManager.match_set_channel, [t.id])
                player: Player = dict_for_kook_id[t.id]
                player_info = PlayerBasicInfo({})
                player_info.score = player.rank
                player_info.user_id = t.id
                player_info.kook_name = t.username

                player_info.first_troop = player.first_troop
                player_info.second_troop = player.second_troop

                player_list.append(player_info)

        except Exception as e:
            LogHelper.log(f"没有注册 {t.id} {t.username}")
            await es_channels.command_channel.send(f'(met){t.id}(met) 你没有注册，请先注册')
            await move_a_to_b_ex(ChannelManager.match_set_channel, [t.id])
            return

        if len(player_list) < 12:
            await msg.reply(f'注册人数不足12，请大伙先注册，/help可以提供支持')
            return
        # 说明注册人数 >=12
        if len(player_list) % 2 != 0:
            await msg.reply(f'人数非奇数！')
            return
        #     player_list.pop()

        divide_data: DivideData = MatchState.divide_player_ex(player_list)
        # print(divide_data.attacker_list)
        # print(divide_data.defender_list)
        await msg.reply(CardMessage(
            Card(
                Module.Header('分队情况表'),
                Module.Divider(),
                Module.Header(f'时间:{get_time_str()}'),
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(divide_data.get_attacker_names(), type=Types.Text.KMD),
                        Element.Text(divide_data.get_attacker_scores(), type=Types.Text.KMD),
                        Element.Text('game_info', type=Types.Text.KMD),
                    )
                ),
                Module.Divider(),
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(divide_data.get_defender_names(), type=Types.Text.KMD),
                        Element.Text(divide_data.get_defender_scores(), type=Types.Text.KMD),
                        Element.Text('game_info', type=Types.Text.KMD),
                    )
                ),
            )
        ))
        if is_no_move != 1:
            await move_a_to_b_ex(ChannelManager.match_attack_channel, divide_data.attacker_list)
            await move_a_to_b_ex(ChannelManager.match_defend_channel, divide_data.defender_list)
        else:
            LogHelper.log("不移动")

        await msg.reply('分配完毕!')

    async def move_a_to_b(a: str, b: str):
        channel = await bot.client.fetch_public_channel(a)
        channel_b = await bot.client.fetch_public_channel(b)
        k = await channel.fetch_user_list()
        for id, user in enumerate(k):
            d: GuildUser = user
            await channel_b.move_user(ChannelManager.match_wait_channel, d.id)

    async def move_a_to_b_ex(b: str, list_player: list):
        channel_b = await bot.client.fetch_public_channel(b)
        for id, user_id in enumerate(list_player):
            await channel_b.move_user(b, user_id)

    @bot.command(name='change_name', case_sensitive=False, aliases=['cn'])
    async def change_name(msg: Message, new_name: str, *args):
        # 处理玩家随便输入的时候， 在函数原型中加入 , *args
        sqlSession.commit()
        t: Player = sqlSession.query(Player).filter(Player.kookId == msg.author_id).first()
        if t:
            player: Player = t
            player_change_names_obj = sqlSession.query(DB_PlayerChangeNames).filter(
                DB_PlayerChangeNames.kookId == msg.author_id).first()
            if player_change_names_obj:
                change_names_obj: DB_PlayerChangeNames = player_change_names_obj
                if change_names_obj.left_times > 0:
                    change_names_obj.lastKookName = new_name
                    player.kookName = new_name
                    change_names_obj.left_times -= 1
                    sqlSession.commit()
                    await msg.reply(f'名称更新成功, ->{new_name}, 剩余次数:{change_names_obj.left_times}')
                else:
                    await msg.reply(f'名称更新失败 。 次数用尽')
                    return
                    pass
            else:
                x = DB_PlayerChangeNames()
                x.kookId = player.kookId
                x.kookName = player.kookName
                x.lastKookName = player.kookName
                x.playerId = player.playerId
                sqlSession.add(x)
                sqlSession.commit()
                await msg.reply(f'名称更新失败 。 次数用尽')
        else:
            await msg.reply('你还未注册，该指令不生效')

    @bot.command(name='type', case_sensitive=False, aliases=['t'])
    async def set_player_type(msg: Message, *args):
        c8 = Card(
            Module.Header('第一兵种选择'),
            Module.ActionGroup(
                Element.Button("步兵", value='f1', click=Types.Click.RETURN_VAL, theme=Types.Theme.INFO),
                Element.Button("骑兵", value='f2', click=Types.Click.RETURN_VAL, theme=Types.Theme.DANGER),
                Element.Button("射手", value='f3', click=Types.Click.RETURN_VAL, theme=Types.Theme.SECONDARY)
            ),
            Module.Divider(),
            Module.Header('第二兵种选择'),
            Module.ActionGroup(
                Element.Button("步兵", value='s1', click=Types.Click.RETURN_VAL, theme=Types.Theme.INFO),
                Element.Button("骑兵", value='s2', click=Types.Click.RETURN_VAL, theme=Types.Theme.DANGER),
                Element.Button("射手", value='s3', click=Types.Click.RETURN_VAL, theme=Types.Theme.SECONDARY)
            ),
        )
        await msg.reply(CardMessage(c8))

    def get_troop_type_name(a: int):
        if a == 1:
            return "步兵"
        elif a == 2:
            return "骑兵"
        elif a == 3:
            return "射手"
        else:
            return "未选择"

    @bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
    async def btn_click_event(b: Bot, e: Event):
        """按钮点击事件"""
        print(e.target_id)
        print(e.body, "\n")
        value = str(e.body['value'])
        user_id = e.body['user_id']
        guild_id = e.body['guild_id']

        if value.startswith('{'):
            btn_value_dict: dict = json.loads(value)
            if 'type' in btn_value_dict.keys():
                type = str(btn_value_dict.get('type', 'invalid'))
                selected_players = btn_value_dict.get('kookId')
                if type == 'match_select_players':
                    selectPlayerMatchData: SelectPlayerMatchData = MatchConditionEx.blmm_1
                    if user_id in '482714005':
                        selectPlayerMatchData.first_team_player_ids.append(selected_players)
                    elif user_id in '1555061634':
                        selectPlayerMatchData.second_team_player_ids.append(selected_players)
                    else:
                        print('你不是队长，禁止选取队员')
                    selectPlayerMatchData.need_to_select = selectPlayerMatchData.need_to_select.remove(selected_players)
        elif value == AdminButtonValue.Refresh_Server_Force:
            if user_id not in ChannelManager.manager_user_id:
                channel = await b.client.fetch_public_channel(ChannelManager.get_command_channel_id(guild_id))
                await channel.send(
                    f'(met){user_id}(met) 禁止使用管理员指令')
                return

        elif value == AdminButtonValue.Refresh_Server_Force or value == AdminButtonValue.Refresh_Server6_Force:
            channel = await b.client.fetch_public_channel(ChannelManager.get_command_channel_id(guild_id))
            if user_id not in ChannelManager.manager_user_id:
                await channel.send(f'(met){user_id}(met) 禁止使用管理员指令')
                return
            if value == AdminButtonValue.Refresh_Server_Force:
                ServerManager.RestartBLMMServer(5)
            else:
                ServerManager.RestartBLMMServer(6)
            await channel.send(f'(met){user_id}(met) 服务器重启成功')

        else:
            with get_session() as sql_session:
                t = sql_session.query(Player).filter(Player.kookId == user_id)
                channel = await b.client.fetch_public_channel(ChannelManager.get_command_channel_id(guild_id))

                if t.count() == 1:
                    player: Player = t.first()

                    is_first_troop = False
                    if value.startswith('f'):
                        troop_type = int(value[1])
                        player.first_troop = troop_type
                        is_first_troop = True
                    elif value.startswith('s'):
                        troop_type = int(value[1])
                        player.second_troop = troop_type
                    troop_name = get_troop_type_name(troop_type)

                    try:
                        sql_session.merge(player)
                        sql_session.commit()
                        await channel.send(
                            f'(met){user_id}(met) 你设置了你的第{1 if is_first_troop else 2}兵种为{troop_name}')
                    except Exception as e:
                        await channel.send(
                            f'(met){user_id}(met) 机器人异常，联系管理员')
                        sql_session.rollback()

                else:
                    await channel.send(
                        f'(met){user_id}(met) 你没有注册，请先注册')

    @bot.command(name='score', case_sensitive=False, aliases=['s'])
    async def show_score(msg: Message, *args):
        # 处理玩家随便输入的时候， 在函数原型中加入 , *args
        sql_session = get_session()
        t = sql_session.query(Player).filter(Player.kookId == msg.author_id)
        if t.count() == 1:
            player: Player = t.first()

            db_playerdata = sql_session.query(DB_PlayerData).filter(DB_PlayerData.playerId == player.playerId)
            if db_playerdata.count() >= 1:
                db_player: DB_PlayerData = db_playerdata.first()
                player.rank = db_player.rank

            cm = CardMessage()
            rank_name = get_rank_name(player.rank)
            c1 = Card(
                Module.Header("基本信息"),
                Module.Context(f'playerId:{player.playerId}'),
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(
                            f"名字:\n{player.kookName}",
                            type=Types.Text.KMD),
                        Element.Text(f"分数:\n{player.rank}", type=Types.Text.KMD),
                        Element.Text(f"位阶:\n(font){rank_name}(font)[pink]",
                                     type=Types.Text.KMD),
                    )
                ),
                # ChannelManager.emoji_farmer
                Module.Divider(),
                Module.Section(
                    Element.Text(f'(font){rank_name}(font)[pink]({player.rank})', type=Types.Text.KMD),
                    Element.Image(src=kim(rank_name), size=Types.Size.LG),
                    mode=Types.SectionMode.LEFT
                ),
                Module.Divider(),
                Module.Section(
                    Element.Text(f'第(font)一(font)[pink]兵种', type=Types.Text.KMD),
                    Element.Image(src=get_troop_type_image(player.first_troop), size=Types.Size.LG),
                    mode=Types.SectionMode.LEFT
                ),
                Module.Section(
                    Element.Text(f'第(font)2(font)[warning]兵种', type=Types.Text.KMD),
                    Element.Image(src=get_troop_type_image(player.second_troop), size=Types.Size.LG),
                    mode=Types.SectionMode.LEFT
                )
            )
            Kill_Info = f'''**Kill Info**
        击杀:{player.kill}
        死亡:{player.death}
        助攻:{player.assist}
        KDA:{(player.kill + player.assist) / max(player.death, 1)}
        KD: {player.kill / max(player.death, 1)}
        伤害:
        '''

            game_info = f'''**游戏**
        对局数:{player.match}
        胜场:{player.win}
        败场:{player.lose}
        平局:{player.draw}
        胜/败:{player.win / max(player.lose, 1)}
        MVPs:{0}
                '''
            c2 = Card(
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(Kill_Info, type=Types.Text.KMD),
                        Element.Text(game_info, type=Types.Text.KMD),
                        Element.Text(f"**步/骑/弓弩**\n{player.infantry}/{player.cavalry}/{player.archer}",
                                     type=Types.Text.KMD),
                    )
                )
            )
            # cm.append(c1)
            cm.append(c1)
            cm.append(c2)
            await  msg.reply(cm)
        else:
            await msg.reply("请先注册")

        pass


def convert_timestamp(timestamp):
    from datetime import datetime
    # 将毫秒时间戳转换为秒
    seconds = timestamp / 1000
    # 使用 datetime.fromtimestamp() 将秒级时间戳转换为 datetime 对象
    dt_object = datetime.fromtimestamp(seconds)
    # 格式化 datetime 对象为 24 小时制的字符串
    formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time


if __name__ == '__main__':
    timestamp = 1721137013547
    print(convert_timestamp(timestamp))
