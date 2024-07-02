DIALECT = "mysql"
DRIVER = "pymysql"
HOST = ""
PORT = 3306
DATABASE = "blmm"
USERNAME = "root"
PASSWORD = "root"

CWMM_SERVER_LIST = []
CWMM_SERVER_NAMES = ["CN_CWMM_1", "CN_CWMM_2", "CN_CWMM_3",
                     "CN_CWMM_4", "CN_CWMM_5", "CN_CWMM_6",
                     "CN_CWMM_7", "CN_CWMM_8", "CN_CWMM_9"]
LEADERBOARD_UPDATE_INTERVAL_SECONDS = 600
HEARTBEAT_ALIVE_SECONDS = 3
ONLINE_INFO_UDPATE_INTERVAL_SECONDS = 10
BROADCAST_MESSAGE_NAME = "系统"
ALLOW_OFFLINE_SERVERS = False
ALLOW_TEST_MODES_FOR_EVERYONE = False

MATCH_WAIT_READY_SECONDS = 30
MATCH_PICK_TEAMMATE_SECONDS = 20
MATCH_WAIT_START_SECONDS = 180
MATCH_RESULT_SHOW_SECONDS = 10
NEXT_MATCH_START_WAIT_SECONDS = 10

SERVER_TICK_IDLE_SECONDS = 90

RANKS = [
    {
        "level": 11,
        "name": "皇帝",
        "rank": 5000,
    }, {
        "level": 10,
        "name": "国王",
        "rank": 4500,
    }, {
        "level": 9,
        "name": "王子",
        "rank": 4000,
    }, {
        "level": 8,
        "name": "公爵",
        "rank": 3500,
    }, {
        "level": 7,
        "name": "领主",
        "rank": 3000,
    }, {
        "level": 6,
        "name": "大骑士",
        "rank": 2500,
    }, {
        "level": 5,
        "name": "骑士",
        "rank": 2000,
    }, {
        "level": 4,
        "name": "侍从",
        "rank": 1500,
    }, {
        "level": 3,
        "name": "守卫",
        "rank": 1200,
    }, {
        "level": 2,
        "name": "农民",
        "rank": 800,
    }, {
        "level": 1,
        "name": "小丑",
        "rank": 0,
    }
]

MATCH_MODES = [
    {
        "id": 1,  # 此id禁止修改
        "name": "近战3V3",
        "description": "在竞技场内与敌人决一死战（此模式拥有单独的排位分，但其他胜场、负场、伤害等数据均不会被统计到个人数据）",
        "count": 3,
        "choose": [1, 2, 1],
        "limit": {"closed": [0, 3, 0], "open": [0, 3, 0]},
    },
    {
        "id": 2,
        "name": "竞技6V6",
        "description": "考验团队配合",
        "count": 6,
        "choose": [1, 2, 2, 1, 1, 2, 1],
        "limit": {"closed": [2, 5, 2], "open": [2, 3, 3]},
    },
    {
        "id": 3,
        "name": "比赛8V8",
        "description": "8人模式",
        "count": 8,
        "choose": [1, 2, 2, 1, 1, 1, 1, 1, 1, 2, 1],
        "limit": {"closed": [3, 6, 3], "open": [3, 4, 4]},
    },
    {
        "id": 4,
        "name": "测试1v1",
        "description": "测试",
        "count": 1,
        "choose": [],
        "limit": {"closed": [0, 1, 0], "open": [0, 1, 0]},
    },
    {
        "id": 5,
        "name": "测试2v2",
        "description": "测试",
        "count": 2,
        "choose": [1, 1],
        "limit": {"closed": [1, 2, 1], "open": [1, 2, 1]},
    },
]

# 封闭图：6人，2射5步2骑；8人，3射6步3骑
# 开阔图：6人，2射3步3骑；8人，3射4步4骑
MAPS = [
    {
        "id": 507,
        "name": "竞技场",
        "type": "closed",
        "modes": [4, 5],
    },
    {
        "id": 577,
        "name": "The Cage",
        "type": "closed",
        "modes": [1],
    },
    {
        "id": 563,
        "name": "维洛伦",
        "type": "closed",
        "modes": [2, 3],
    },
    {
        "id": 564,
        "name": "卡斯特卢",
        "type": "open",
        "modes": [2, 3],
    },
    {
        "id": 565,
        "name": "虔信村",
        "type": "open",
        "modes": [2, 3],
    },
    {
        "id": 566,
        "name": "荣耀堡",
        "type": "closed",
        "modes": [2, 3],
    },
    {
        "id": 567,
        "name": "沙漠堡",
        "type": "closed",
        "modes": [2, 3],
    },
    {
        "id": 568,
        "name": "天茶镇",
        "type": "closed",
        "modes": [2, 3],
    },
    # {
    #    "id": 569,
    #    "name": "河畔村",
    #    "type": "open",
    #    "modes": [2, 3],
    # },
    {
        "id": 570,
        "name": "凌霜圣地",
        "type": "open",
        "modes": [2, 3],
    },
    {
        "id": 571,
        "name": "咸鱼镇",
        "type": "closed",
        "modes": [2, 3],
    },
    {
        "id": 572,
        "name": "海军哨所",
        "type": "closed",
        "modes": [2, 3],
    },
    {
        "id": 573,
        "name": "绿洲瀑布",
        "type": "open",
        "modes": [2, 3],
    },
    {
        "id": 574,
        "name": "诺德城镇",
        "type": "closed",
        "modes": [2, 3],
    },
    {
        "id": 575,
        "name": "山中堡垒",
        "type": "closed",
        "modes": [2, 3],
    },
    # {
    #    "id": 576,
    #    "name": "凛冬堡",
    #    "type": "closed",
    #    "modes": [2, 3],
    # },
    {
        "id": 578,
        "name": "三角村",
        "type": "closed",
        "modes": [2, 3],
    },
    {
        "id": 579,
        "name": "径流",
        "type": "open",
        "modes": [2, 3],
    },
    {
        "id": 580,
        "name": "斯瓦迪亚城镇",
        "type": "closed",
        "modes": [2, 3],
    },
    # {
    #    "id": 581,
    #    "name": "新废墟",
    #    "type": "open",
    #    "modes": [2, 3],
    # },
]
