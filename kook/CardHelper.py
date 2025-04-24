from khl.card import CardMessage, Card, Module, Element, Struct, Types

from config import get_rank_name
from init_db import get_session
from kook.ChannelKit import kim, get_troop_type_image
from tables import DB_Player, DB_PlayerData
from tables.PlayerMedal import DB_PlayerMedal

word_dict = {
    '恶霸': 'XErBa',
    "城管": 'CenGua',
}


def replace_sensitive_words(text: str) -> str:
    """
    Replace sensitive words in the input text with their corresponding placeholders.

    Args:
        text: Input string potentially containing sensitive words

    Returns:
        String with sensitive words replaced by their placeholders
    """
    if not isinstance(text, str):
        return text

    for word, placeholder in word_dict.items():
        text = text.replace(word, placeholder)
    return text


async def get_score_list_card():
    cm = CardMessage()

    sqlSession = get_session()
    sqlSession.commit()

    t = sqlSession.query(DB_PlayerData).order_by(DB_PlayerData.rank.desc()).limit(10).all()
    # print(t)
    kill_scoreboard = '**积分榜单**'
    for id, k in enumerate(t):
        # player: Player = k
        player_data: DB_PlayerData = k
        kill_scoreboard += f"\n{player_data.playerName}:{player_data.rank}"

    game_scoreboard = '**对局榜单**'
    t = sqlSession.query(DB_PlayerData).order_by(DB_PlayerData.win.desc()).limit(10).all()
    for id, k in enumerate(t):
        player: DB_PlayerData = k
        game_scoreboard += f"\n{player.playerName}:{player.win}"

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
    return cm


async def get_player_score_card(kook_id: str):
    sql_session = get_session()
    sql_session.autoflush()
    t = sql_session.query(DB_Player).filter(DB_Player.kookId == kook_id)
    if t.count() == 1:
        player: DB_Player = t.first()

        db_playerdata = sql_session.query(DB_PlayerData).filter(DB_PlayerData.playerId == player.playerId)
        if db_playerdata.count() >= 1:
            db_player: DB_PlayerData = db_playerdata.first()
            player.rank = db_player.rank
        else:
            db_player = player
        sql_session.commit()

        # 获取玩家 勋章
        player_medal_db = sql_session.query(DB_PlayerMedal).filter(DB_PlayerMedal.kookId == kook_id)
        if player_medal_db.count() == 1:
            player_medal_db: DB_PlayerMedal = player_medal_db.first()
        else:
            player_medal_db = DB_PlayerMedal()
            player_medal_db.playerId = db_player.playerId
            player_medal_db.kookId = player.kookId
            sql_session.add(player_medal_db)
            sql_session.commit()

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
    击杀:{db_player.kill}
    死亡:{db_player.death}
    助攻:{db_player.assist}
    KDA:{round((db_player.kill + db_player.assist) / max(db_player.death, 1), 3)}
    KD: {round(db_player.kill / max(db_player.death, 1), 3)}
    伤害:{db_player.damage}
    '''

        game_info = f'''**游戏**
    对局数:{db_player.match}
    胜场:{db_player.win}
    败场:{db_player.lose}
    平局:{db_player.draw}
    胜/败:{round(db_player.win / max(db_player.lose, 1), 3)}
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
            ),
            Module.Divider(),
            Module.Section(
                Struct.Paragraph(
                    3,
                    Element.Text(player_medal_db.get_testor_emoji)
                )
            )
        )
        # cm.append(c1)
        cm.append(c1)
        cm.append(c2)
        return cm
    else:
        return "请先注册"
