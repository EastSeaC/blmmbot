import aiohttp

baseUrl = "https://www.kookapp.cn/api/v3/"
baseUrl2 = "https://www.kookapp.cn"


class UrlHelper:
    baseUrl2 = "https://www.kookapp.cn"

    user_list = baseUrl2 + '/api/v3/channel/user-list'
    move_user = baseUrl2 + '/api/v3/channel/move-user'
    delete_message = baseUrl2 + '/api/v3/message/delete'

    local_url = "http://localhost:14725/"
    reg_url = local_url + 'reg/'


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
