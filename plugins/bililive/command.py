import asyncio
import aiofiles
from os import path

import requests
from nonebot import CommandSession, on_command
from nonebot.argparse import ArgumentParser
from nonebot.permission import *

try:
    import ujson
except:
    import json as ujson

USAGE = r'''！群订阅 <房间号> 增加本群订阅
！群订阅列表 <SUPERUSER可选:全部> 展示本群(全部群)所有订阅
！群取消订阅 <房间号> 删除本群订阅'''

config_file = path.join(path.dirname(__file__), 'bililiveconfig.json')


# 增加订阅
@on_command('addlive', aliases=('群订阅'), only_to_me=False, shell_like=True, permission=GROUP_ADMIN | SUPERUSER)
async def addlive(session: CommandSession):
    parser = ArgumentParser(session=session, usage=USAGE)
    parser.add_argument('room_id', type=str, nargs=1)
    args = parser.parse_args(session.argv)
    group_id = session.event.group_id

    # 检查直播间是否存在
    room_id = args.room_id[0]
    check_room_id = 'https://api.live.bilibili.com/room/v1/Room/room_init?id=' + room_id
    loop = asyncio.get_running_loop()
    url = await loop.run_in_executor(None, requests.get, check_room_id)
    response = ujson.loads(url.text)
    if response['code'] != 0:
        session.finish('该直播间不存在')

    async with aiofiles.open(config_file, 'r', encoding='utf-8') as f:
        data = ujson.loads(await f.read())

    flag = 1
    for index, member in enumerate(data):
        if room_id == member['room_id'] and group_id in member['group_ids']:
            session.finish('本群已订阅此直播，无需重复添加')
        # 直播间已记录，新增群号
        elif room_id == member['room_id'] and group_id not in member['group_ids']:
            member['group_ids'].append(group_id)
            data[index] = member
            flag = 0
            break

    # 新增直播间
    if flag:
        new_member = {
            "room_id": room_id,
            "live_status": 0,
            "group_ids": [
                group_id
            ]
        }
        data.append(new_member)

    async with aiofiles.open(config_file, 'w', encoding='utf-8') as f:
        await f.write(ujson.dumps(data, indent=4))

    name = await get_name(str(response['data']['room_id']))
    success_message = f'已成功订阅{name}的直播'
    session.finish(success_message)


# 查询订阅
@on_command('listlive', aliases=('群订阅列表'), only_to_me=False, permission=GROUP_ADMIN | SUPERUSER)
async def listlive(session: CommandSession):
    mode = session.get('mode')
    group_id = session.event.group_id
    async with aiofiles.open(config_file, 'r', encoding='utf-8') as f:
        data = ujson.loads(await f.read())
    if mode == 'all' or mode == '全部':
        msg = '所有的直播间：'
        for member in data:
            await asyncio.sleep(0.2)    # 并发高b站会ban，极限大概在一秒7次左右
            room_id = member['room_id']
            name = await get_name(room_id)
            group_ids = '、'.join([str(group_id)
                                  for group_id in member['group_ids']])
            msg += (f'\n{name}：{room_id}，在群{group_ids}')
        session.finish(msg)

    ls = []
    for member in data:
        if group_id in member['group_ids']:
            ls.append(member)

    msg = '本群订阅的直播间有：'
    for member in ls:
        await asyncio.sleep(0.2)    # 并发高b站会ban，极限大概在一秒7次左右
        room_id = member['room_id']
        name = await get_name(room_id)
        msg += ('\n' + name + '：' + room_id)

    if msg == '本群订阅的直播间有：':
        session.finish('本群还未订阅任何直播间')

    session.finish(msg)


@listlive.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['mode'] = stripped_arg
        else:
            session.state['mode'] = ''


# 删除订阅
@on_command('removelive', aliases=('群取消订阅','群删除订阅'), only_to_me=False, shell_like=True, permission=GROUP_ADMIN | SUPERUSER)
async def removelive(session: CommandSession):
    parser = ArgumentParser(session=session)
    parser.add_argument('room_id', type=str, nargs=1)
    args = parser.parse_args(session.argv)
    room_id = args.room_id[0]
    group_id = session.event.group_id

    async with aiofiles.open(config_file, 'r', encoding='utf-8') as f:
        data = ujson.loads(await f.read())

    for index, member in enumerate(data):
        if room_id == member['room_id'] and group_id in member['group_ids']:
            member['group_ids'].remove(group_id)
            # 如果删掉了最后一个群，就连这个直播间一起消灭
            if not member['group_ids']:
                data.pop(index)
            else:
                data[index] = member

            async with aiofiles.open(config_file, 'w', encoding='utf-8') as f:
                await f.write(ujson.dumps(data, indent=4))
            session.finish('已成功删除')

    session.finish('本群内找不到该房间号，请用listlive命令检查')


# 根据房间号获得up主名字
async def get_name(room_id):
    info_api = 'https://api.live.bilibili.com/room/v1/Room/get_info?room_id=' + room_id
    loop = asyncio.get_running_loop()
    url2 = await loop.run_in_executor(None, requests.get, info_api)
    response = url2.json()
    uid = response['data']['uid']
    name_api = 'http://api.bilibili.com/x/space/acc/info?mid=' + str(uid)
    loop = asyncio.get_running_loop()
    url3 = await loop.run_in_executor(None, requests.get, name_api)
    response = url3.json()
    name = response['data']['name']
    return name
