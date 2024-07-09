from khl import Bot, Message
from khl.card import CardMessage, Card, Module, Struct, Element, Types

from config import get_rank_name
from init_db import get_session
from kook.ChannelKit import EsChannels
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
                Module.Section(
                    Struct.Paragraph(
                        3,
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
