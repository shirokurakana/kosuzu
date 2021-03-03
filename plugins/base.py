from nonebot import CommandSession, on_command
from nonebot.message import unescape
from nonebot.permission import *


@on_command('echo',
            permission=SUPERUSER,
            only_to_me=False)
async def echo(session: CommandSession):
    await session.send(
        session.state.get('message') or session.current_arg)


@on_command('say',
            permission=SUPERUSER,
            only_to_me=False)
async def say(session: CommandSession):
    await session.send(
        unescape(session.state.get('message') or session.current_arg))


@on_command('test',
            permission=SUPERUSER,
            aliases=('ping', '测试'),
            only_to_me=False)
async def test(session: CommandSession):
    await session.send('XD')
