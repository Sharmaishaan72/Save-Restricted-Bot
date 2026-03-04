# commands related to config change - changing stringsession , or maybe more in future 
# TODO : add multiple account support

import json

from pyrogram import Client
from pyrogram import filters

from .. import config 
from ..config import open_config
from ..client import restart_account
from ..wrappers.access_only import access_only


@Client.on_message(filters.command(["string"]))
@access_only
async def set_string_session(client: Client, message):
	print("recieved change req")
	DATA = open_config()
	if len(message.command) < 2:
		await client.send_message(message.chat.id, "__Usage__: `/string NEW_STRING_SESSION`", reply_to_message_id=message.id)
		return
	DATA["STRING"] = message.command[1].strip()
	with open("config.json", "w") as f:
		json.dump(DATA, f, indent=4)
	msg = await client.send_message(message.chat.id, "**STRING session updated.**", reply_to_message_id=message.id)
	config.config.reload_env()
	await restart_account()
	await msg.edit("**String session Updated successfully!**")


@Client.on_message(filters.command(["addaccess"]))
@access_only
async def add_access(client: Client, message):
	DATA = open_config()
	if len(message.command) < 2:
		await client.send_message(message.chat.id, "__Usage__: `/addaccess {user_id}`", reply_to_message_id=message.id)
		return
	old = DATA['OWNER_USERIDS']
	DATA["OWNER_USERIDS"] = old + "," + message.command[1].strip()
	with open("config.json", "w") as f:
		json.dump(DATA, f, indent=4)
	msg = await client.send_message(message.chat.id, "**updating...**", reply_to_message_id=message.id)
	config.config.reload_env()
	await msg.edit("**list updated! They can access the bot now**")
	await client.send_message(int(message.command[1].strip()), "You have been allowed to access the bot by the owner , you can use it now")
	print(config.config.owner_ids)




	
	