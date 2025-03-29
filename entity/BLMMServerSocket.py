import asyncio
import json

from lib.LogHelper import LogHelper


class SocketKeyNames:
    type = 'type'

    pass


class AsyncSocketServer:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port

    async def handle_client(self, reader, writer):
        """
        处理客户端连接
        """
        client_address = writer.get_extra_info('peername')
        print(f"Socket 服务器: 已连接到 {client_address}")

        while True:
            # 接收数据
            data = await reader.read(1024)
            if not data:
                # 如果没有数据，关闭连接
                print(f"Socket 服务器: 与 {client_address} 的连接已关闭")
                writer.close()
                await writer.wait_closed()
                break

            # 处理数据
            message = data.decode('utf-8')
            print(f"Socket 服务器: 收到来自 {client_address} 的数据: {message}")

            json_obj = json.loads(message)
            if SocketKeyNames.type in json_obj:
                type_a = json_obj[SocketKeyNames.type]

                if type_a == 'cancel-match':
                    LogHelper.log('取消比赛')

            # 发送响应
            writer.write(data)
            await writer.drain()

    async def start_server(self):
        """
        启动异步 Socket 服务器
        """
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )

        addr = server.sockets[0].getsockname()
        print(f"Socket 服务器: 正在 {addr} 上监听...")

        async with server:
            await server.serve_forever()
