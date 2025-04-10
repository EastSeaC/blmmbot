import asyncio
import json
from typing import Dict, Set

import aiohttp
from aiohttp import web

from lib.LogHelper import LogHelper
from init_db import get_session
from services.DataSyncService import DataSyncService

# 创建事件
match_cancelled_event = asyncio.Event()


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            received_message = msg.data
            print(f"Received: {received_message}")  # 打印接收到的消息到控制台
            try:
                data_str: dict = json.loads(received_message)
                op = data_str.get('op', 'none')

                if op == 'clear':
                    await ws.send_str('已清空')
                elif op == 'sync_base':
                    data_to_send = DataSyncService.get_sync()
                    await ws.send_str(json.dumps({
                        'op': 'sync_base',
                        'data': data_to_send,
                        'type': 'from_main_server',
                    }))
            except Exception as e:
                pass
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print(f"WebSocket Error: {ws.exception()}")

    return ws


if __name__ == '__main__':
    z = DataSyncService.get_admin()
    print(z)

    print(type(z[0]))
