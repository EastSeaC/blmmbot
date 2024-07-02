from aiohttp import web
from io import BytesIO
from openpyxl import Workbook

bp = web.RouteTableDef()


@bp.get('/')
async def px(request):
    return web.Response(text=f'a|{123}')


async def download_excel(request):
    # 创建一个Excel文件
    wb = Workbook()
    ws = wb.active
    ws['A1'] = 'Hello'

    # 将Excel文件内容写入BytesIO对象
    excel_data = BytesIO()
    wb.save(excel_data)
    excel_data.seek(0)

    # 设置响应头信息
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename="example.xlsx"'

    # 将BytesIO对象中的内容作为响应返回
    await response.prepare(request)
    await response.write(excel_data.read())

    return response


app = web.Application()
app.add_routes(bp)
app.router.add_get('/download_excel', download_excel)  # 定义返回Excel文件的路由

web.run_app(app, host='localhost', port=7206)
