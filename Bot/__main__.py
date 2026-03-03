from .client import configure_bot, configure_session

from pyrogram import idle

import asyncio

async def main():
    await configure_session()
    await configure_bot()
    await idle()

asyncio.run(main())




