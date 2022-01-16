from datetime import date
from typing import Optional, Tuple

from httpx import AsyncClient
from nonebot.adapters.onebot.v11.message import MessageSegment
from src.utils.browser import browser

from .config import CITY_MAP


def _get_city(name: str) -> Tuple[bool, Optional[str], Optional[str]]:
    '''
    :说明
        通过name获取参数
    :返回
        * bool：是否是合法参数
        * str：省份名
        * str：城市名
    '''
    city = CITY_MAP.get(name)
    if city is None:
        return False, None, None
    if city == "":
        return True, city, None
    return True, city, name


async def get_data(name: str) -> MessageSegment:
    '''获取数据'''
    flag, province, city = _get_city(name)
    if not flag:
        return MessageSegment.text('查询失败，请检查参数！')
    params = {"province": province}
    if city:
        params['city'] = city

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "Accept-Charset": "utf-8",

    }

    async with AsyncClient(headers=headers) as client:
        url = "https://api.yimian.xyz/coro/"
        try:
            req = await client.get(url=url, params=params)
            result = req.json()
            data = {}
            if city:
                data['name'] = result['cityName']
            else:
                data['name'] = result['provinceName']
            data['currentConfirmedCount'] = result['currentConfirmedCount']  # 现存确诊
            data['confirmedCount'] = result['confirmedCount']  # 累计确诊
            data['suspectedCount'] = result['suspectedCount']  # 疑似病例
            data['curedCount'] = result['curedCount']  # 累计治愈
            data['deadCount'] = result['deadCount']  # 累计死亡
            data['highDangerCount'] = result['highDangerCount']  # 重症病例
        except Exception as e:
            return MessageSegment.text(f"查询失败，{str(e)}")

    time_now = date.today()
    data['time'] = time_now.strftime("%Y-%m-%d")
    pagename = "yiqing.html"
    img = await browser.template_to_image(pagename=pagename, data=data)
    return MessageSegment.image(img)
