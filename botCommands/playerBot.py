from khl import Bot, Message, GuildUser
from khl.card import CardMessage, Card, Module, Struct, Element, Types

from LogHelper import LogHelper
from config import get_rank_name
from init_db import get_session
from kook.ChannelKit import EsChannels, ChannelManager
from match_state import PlayerBasicInfo, DivideData, MatchState
from tables import *

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
    async def es_start_match(msg: Message):
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
        if len(k) % 2 == 1 or len(k) == 0:
            await msg.reply('人数异常')
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
                player_list.append(player_info)

        except Exception as e:
            LogHelper.log(f"没有注册 {t.id} {t.username}")
            await es_channels.command_channel.send(f'(met){t.id}(met) 你没有注册，请先注册')
            await move_a_to_b_ex(ChannelManager.match_set_channel, [t.id])
            return

        if len(player_list) != 12:
            await es_channels.command_channel.send(f'注册人数不足12，请大伙先注册，/help可以提供支持')
            return
            # if len(player_list) % 2 != 0:
        #     player_list.pop()

        divide_data: DivideData = MatchState.divide_player_ex(player_list)
        print(divide_data.attacker_list)
        print(divide_data.defender_list)
        await move_a_to_b_ex(ChannelManager.match_attack_channel, divide_data.attacker_list)
        await move_a_to_b_ex(ChannelManager.match_defend_channel, divide_data.defender_list)

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
            player.kookName = new_name
            sqlSession.commit()
            await msg.reply(f'名称更新成功, ->{new_name}')
        else:
            await msg.reply('你还未注册，该指令不生效')

    @bot.command(name='score', case_sensitive=False, aliases=['s'])
    async def show_score(msg: Message, *args):
        # 处理玩家随便输入的时候， 在函数原型中加入 , *args
        sqlSession.commit()
        t = sqlSession.query(Player).filter(Player.kookId == msg.author_id)
        if t.count() == 1:
            player: Player = t.first()
            cm = CardMessage()
            c1 = Card(
                Module.Header("基本信息"),
                Module.Context(f'playerId:{player.playerId}'),
                Module.Section(
                    Struct.Paragraph(
                        3,
                        Element.Text(f"名字:\n{player.kookName}", type=Types.Text.KMD),
                        Element.Text(f"分数:\n{player.rank}", type=Types.Text.KMD),
                        Element.Text(f"位阶:\n{get_rank_name(player.rank)}", type=Types.Text.KMD),
                    )
                )
            )
            Kill_Info = f'''**Kill Info**
    Kills:{player.kill}
    Deaths:{player.death}
    Assists:{player.assist}
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
