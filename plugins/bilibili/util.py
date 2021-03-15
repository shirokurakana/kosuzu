import asyncio

import requests


async def get_name_by_uid(uid: int) -> str:
    '''根据uid获取昵称'''
    api = f'http://api.bilibili.com/x/space/acc/info?mid={uid}'
    loop = asyncio.get_running_loop()
    resp = await loop.run_in_executor(None, requests.get, api)
    try:
        return resp.json()['data']['name']
    except KeyError:
        return None


async def get_live_status(room_id: str) -> int:
    '''根据room_id(房间号)获取直播间状态'''
    api = f'https://api.live.bilibili.com/room/v1/Room/get_info?room_id={room_id}'
    loop = asyncio.get_running_loop()
    resp = await loop.run_in_executor(None, requests.get, api)
    try:
        return resp.json()['data']['live_status']
    except KeyError:
        return None
