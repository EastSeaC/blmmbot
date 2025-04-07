import json

from aiohttp import web

from entity.webEntity.ControllerResponse import ControllerResponse
from init_db import get_session
from tables.Announcement import DB_Anouncement

matchRouter = web.RouteTableDef()


@matchRouter.get('/get-notice')
async def get_notice_1(req):
    with get_session() as sql_session:
        notices = sql_session.query(DB_Anouncement).where(DB_Anouncement.isShow == 1).all()

        p = []
        for i in notices:
            notice: DB_Anouncement = i
            p.append(notice.to_dict())

        return web.json_response(ControllerResponse.success_response(json.dumps(p)))
