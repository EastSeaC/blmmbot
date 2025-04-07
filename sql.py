# import random
# import string
# from aiomysql import create_pool
# import asyncio
# import aiomysql
#
#
# class DatabaseManager:
#     _instance = None
#     _pool = None
#
#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             cls._instance = super().__new__(cls)
#         return cls._instance
#
#     async def init_pool(self):
#         self._pool = await create_pool(
#             host='localhost',
#             port=3306,
#             user='root',
#             password='root',
#             db='blmm',
#             autocommit=True
#         )
#
#     async def get_connection(self):
#         if not self._pool:
#             await self.init_pool()
#         return await self._pool.acquire()
#
#     async def release_connection(self, conn):
#         await self._pool.release(conn)
#
# # 在其他模块中使用连接池
#
#
# async def some_function():
#     db_manager = DatabaseManager()
#     conn = await db_manager.get_connection()  # 添加 await 关键字
#     try:
#         cursor = await conn.cursor()
#         await cursor.execute('SELECT * FROM players limit 10;')
#         result = await cursor.fetchall()
#         # print(result)
#         for i in result:
#             print(i)
#         await cursor.close()
#     finally:
#         await db_manager.release_connection(conn)
#
#
# def generate_verification_code():
#     # 生成包含数字和大写字母的字符集
#     characters = string.digits + string.ascii_uppercase
#
#     # 从字符集中随机选择6个字符作为验证码
#     verification_code = ''.join(random.choices(characters, k=6))
#
#     return verification_code
#
#
# async def add_player_code(player_info: dict):
#     player_id = player_info["player_id"]
#     user_id = player_info['user_id']
#
#     db_manager = DatabaseManager()
#     conn = await db_manager.get_connection()  # 添加 await 关键字
#
#     code = generate_verification_code()
#     success = False
#     text = ''
#     try:
#         cursor = await conn.cursor()
#         await cursor.execute(f"SELECT count(*) FROM verifs where playerId = '{player_id}' or userId = '{user_id}'")
#         result = await cursor.fetchall()
#         print('z'*30)
#         print(result, result[0], result[0][0])
#         count = result[0][0]
#         if count == 0:
#             await cursor.execute(f"Insert into verifs (playerId,code,userId) values ('{player_id}','{code}','{user_id}')")
#             success = True
#             text = "验证码生成成功，请进入游戏"
#         else:
#             success = False
#             text = "验证码已存在，请不要重复提交请求"
#         await cursor.close()
#         return success, text
#     except Exception as e:
#         await db_manager.release_connection(conn)
#         return False, f"错误{str(e)}"
#     finally:
#         await db_manager.release_connection(conn)
#
#
# async def validate_player_code(player_info: dict):
#     player_id = player_info["player_id"]
#     code = player_info['code']
#     user_id = player_info['user_id']
#     userName = player_info['userName']
#
#     db_manager = DatabaseManager()
#     conn = await db_manager.get_connection()  # 添加 await 关键字
#     try:
#         cursor = await conn.cursor()
#         sql = f"SELECT count(*) FROM verifs where playerId = '{player_id}' and code = '{code}' and userId = '{user_id}' and startTime >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)"
#         await cursor.execute(sql)
#         result = await cursor.fetchall()
#         count = result[0][0]
#         if count == 1:
#             await cursor.execute(f"insert into players (playerId,userId,userName) ('{player_id}','{user_id}','{userName}')")
#             await cursor.execute(f"delete from verifs where playerId = '{player_id}'")
#             text = '注册成功'
#             success = True
#         else:
#             text = '验证码已过期(5分钟)或 无验证码，请重新注册 /help'
#             success = False
#             pass
#         return success, text
#     except Exception as e:
#         return success, str(e)
#     finally:
#         await db_manager.release_connection(conn)
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(some_function())
