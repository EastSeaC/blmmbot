import aiohttp_jinja2
import jinja2
from aiohttp import web
import sys
# 本地文件导出
from web_bp import bp

# 添加routes到app中
app = web.Application()
app.router.add_static('/satic/', './satic', name='satic')
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./satic'))  # 指定模板文件目录
app.add_routes(bp)

# HOST, PORT = '0.0.0.0', 14725
HOST, PORT = 'localhost', 14725
if __name__ == '__main__':
    argv = sys.argv
    if len(argv) > 1:
        new_host = argv[1]
        if new_host is not None:
            HOST = new_host
    web.run_app(app, host=HOST, port=PORT)
