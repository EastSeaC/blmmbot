import asyncio
import json
from asyncio import Queue
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

    async def receive_match_info():
        try:
            while not ws.closed:
                try:
                    message: Queue = request.app['message_queue']
                    if not message.empty():
                        match_info = await message.get()
                        await ws.send_str(json.dumps({'op': 'start_match', 'match_data_x': match_info}))
                    else:
                        await asyncio.sleep(0.25)
                except Exception as e:
                    print(f"Error in receive_match_info: {e}")
                    if not ws.closed:
                        await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("receive_match_info task cancelled")
            raise

    async def handle_client_info():
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    received_message = msg.data
                    print(f"Received: {received_message}")

                    try:
                        if not str(received_message).startswith('{'):
                            continue
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
                        print(f"Error processing message: {e}")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f"WebSocket Error: {ws.exception()}")
        except asyncio.CancelledError:
            print("handle_client_info task cancelled")
            raise
        except Exception as e:
            print(f"Error in handle_client_info: {e}")
            raise

    try:
        done, pending = await asyncio.wait(
            [handle_client_info(), receive_match_info()],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # 取消仍在运行的任务
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Error cancelling task: {e}")

        # 检查是否有任务因异常完成
        for task in done:
            if task.exception():
                print(f"Task failed: {task.exception()}")
    except Exception as e:
        print(f"Error in websocket handler: {e}")
    finally:
        if not ws.closed:
            await ws.close()
        return ws


if __name__ == '__main__':
    z = DataSyncService.get_admin()
    print(z)

    print(type(z[0]))
