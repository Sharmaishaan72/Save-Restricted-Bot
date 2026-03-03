from pyrogram import Client, idle
from .config import config

import logging

logging.basicConfig(
    level=logging.INFO,  # change to INFO if too noisy
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


bot: Client = None
acc: Client = None

async def configure_session():
    global acc
    if config.api_id and config.api_hash and config.ss:
        acc = Client(
            "myacc",
            api_id=config.api_id,
            api_hash=config.api_hash,
            session_string=config.ss
        )
        await acc.start()

async def configure_bot():
    global bot
    if config.api_id and config.api_hash and config.bot_token:
        bot = Client(
            "mybot",
            api_id=config.api_id,
            api_hash=config.api_hash,
            bot_token=config.bot_token,
            plugins=dict(root="Bot/plugins")
        )
        await bot.start()


async def restart_account():
    global acc

    if acc.is_connected:
        await acc.stop()

    await configure_session()