import asyncio
from os import path

import nonebot
import requests
from nonebot import get_bot

from plugins.bilibili.util import get_live_status, get_name_by_uid
from .command import *

try:
    import ujson
except:
    import json as ujson

bot = get_bot()

config_file = path.join(path.dirname(__file__), 'bililiveconfig.json')


@nonebot.scheduler.scheduled_job('interval', minutes=2, max_instances=10)
async def _():

    if not path.isfile(config_file):
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(r'[]')
    with open(config_file, 'r', encoding='utf-8') as f:
        data = ujson.loads(f.read())

    bot = nonebot.get_bot()

    for index, member in enumerate(data):
        await asyncio.sleep(0.5)    # 并发高b站会ban，极限大概在一秒7次左右
        room_id = member['room_id']
        live_status = member['live_status']
        group_ids = member['group_ids']
        now_status = await get_live_status(room_id)

        if live_status == now_status:
            # 直播状态没有变化，跳过
            continue

        member['live_status'] = now_status
        data[index] = member
        async with aiofiles.open(config_file, 'w', encoding='utf-8') as f:
            await f.write(ujson.dumps(data, indent=4))

        if now_status == 1:
            # 开播（非1→1）
            online = True
        elif live_status == 1:
            # 下播（1→非1）
            online = False
        else:
            # 其他情况，跳过
            continue
        message = await get_info(room_id, online)

        for group_id in group_ids:
            if group_id in bot.config.bililive_at_all_list:
                if '开始了' in message.splitlines()[0]:
                    message = '[CQ:at,qq=all]' + message
            await bot.send_group_msg(group_id=group_id, message=message)


async def get_info(room_id: str, online: bool) -> str:
    # 获取直播间信息
    info_api = 'https://api.live.bilibili.com/room/v1/Room/get_info?room_id=' + room_id
    loop = asyncio.get_running_loop()
    url2 = await loop.run_in_executor(None, requests.get, info_api)
    data = url2.json()['data']
    user_cover = data['user_cover']
    keyframe = data['keyframe']
    uid = data['uid']
    title = data['title']
    link = 'https://live.bilibili.com/' + room_id

    # 通过uid获取name
    name = await get_name_by_uid(uid)

    if online:
        # 通过keyframe获取封面图
        if user_cover:
            pic = f'当前直播间封面：[CQ:image,file={user_cover}]'
        else:
            pic = f'上次直播关键帧：[CQ:image,file={keyframe}]'
        message = f'{name}的直播开始了\n{pic}{title}\n{link}'
    else:
        message = (
            f'{name}的直播结束了\n上次直播关键帧：[CQ:image,file={keyframe}]{title}\n{link}')
    return message
