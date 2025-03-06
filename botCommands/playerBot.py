import json
import re

from khl import Bot, Message, GuildUser, EventTypes, Event, PublicVoiceChannel
from khl.card import CardMessage, Card, Module, Struct, Element, Types

from botCommands.ButtonValueImpl import AdminButtonValue, PlayerButtonValue
from lib.LogHelper import LogHelper, get_time_str
from config import get_rank_name
from init_db import get_session
from kook.ChannelKit import EsChannels, ChannelManager, kim, get_troop_type_image, OldGuildChannel
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

    @bot.command(name='e', case_sensitive=False, aliases=['e'])
    async def es_start_match(msg: Message, is_no_move: int = 0):
        """
        开启匹配指令
        is_no_move: 1 表示 不移动玩家，仅用作测试
        """
        if ChannelManager.is_common_user(msg.author_id):
            await msg.reply('禁止使用es指令')
            return
        try:
            sqlSession.commit()
        except Exception as e:
            await msg.reply('数据库提交异常')
            sqlSession.rollback()

        # k: PublicVoiceChannel = await bot.client.fetch_public_channel(OldGuildChannel.match_wait_channel)
        # k = await k.fetch_user_list()
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

        print('this is z data')
        print([i.__dict__ for i in z])
        print('this is dict_for_kook_id')
        print([i.__dict__ for i in dict_for_kook_id.values()])
        try:
            for id, user in enumerate(k):
                t: GuildUser = user
                if t.id not in dict_for_kook_id:
                    await es_channels.command_channel.send(f'(met){t.id}(met) 你没有注册，请先注册')
                    await move_a_to_b_ex(OldGuildChannel.match_set_channel, [t.id])
                player: Player = dict_for_kook_id[t.id]
                player_info = PlayerBasicInfo({'username': player.kookName})
                player_info.score = player.rank
                player_info.user_id = player.kookId
                player_info.username = player.kookName
                player_info.player_id = player.playerId
                # print(player_info.username)
                player_list.append(player_info)

        except Exception as e:
            print(repr(e))
            LogHelper.log(f"没有注册 {t.id} {t.username}")
            await es_channels.command_channel.send(f'(met){t.id}(met) 你没有注册，请先注册 Exception!')
            await move_a_to_b_ex(ChannelManager.match_set_channel, [t.id])
            return

        # if len(player_list) < 12:
        #     await msg.reply(f'注册人数不足12，请大伙先注册，/help可以提供支持')
        #     return
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
            await move_a_to_b_ex(OldGuildChannel.match_attack_channel, divide_data.attacker_list)
            await move_a_to_b_ex(OldGuildChannel.match_defend_channel, divide_data.defender_list)
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

    @bot.on_message()
    async def kook_bot_message(m: Message):
        print('123123x')
        bot_id = (await bot.client.fetch_me()).id

        print(bot_id)
        a = re.search(f'\(met\){bot_id}\(met\)', m.content)
        if a is None:
            return

        c7 = Card(
            Module.Header('玩家帮助菜单'),
            Module.Divider(),
            Module.ActionGroup(
                Element.Button("查看服务器状态", value=PlayerButtonValue.player_wonder_server_state
                               , click=Types.Click.RETURN_VAL, theme=Types.Theme.INFO),
                Element.Button("查看分数", value=PlayerButtonValue.player_score, click=Types.Click.RETURN_VAL,
                               theme=Types.Theme.DANGER),
                Element.Button("查看排行榜", value=PlayerButtonValue.player_score_list, click=Types.Click.RETURN_VAL,
                               theme=Types.Theme.SECONDARY)
            )
        )
        await m.reply(CardMessage(c7))

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
