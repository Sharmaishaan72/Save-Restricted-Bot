# thumbnail management commands

import os

from pyrogram import Client, filters
from pyrogram.types import ReplyParameters

from .. import config
from ..wrappers.access_only import access_only

THUMB_PATH = "thumb.jpg"


@Client.on_message(filters.command(["setthumb"]))
@access_only
async def set_thumb(client: Client, message):
	if not message.reply_to_message or not message.reply_to_message.photo:
		await client.send_message(
			message.chat.id,
			"__Reply to a **photo** with /setthumb to set it as the custom thumbnail.__",
			reply_parameters=ReplyParameters(message_id=message.id)
		)
		return

	msg = await client.send_message(message.chat.id, "__Downloading thumbnail...__", reply_parameters=ReplyParameters(message_id=message.id))

	# Download the replied-to photo to a temp path, then rename to thumb.jpg
	downloaded = await client.download_media(message.reply_to_message.photo.file_id)
	if os.path.exists(THUMB_PATH):
		os.remove(THUMB_PATH)
	os.rename(downloaded, THUMB_PATH)

	await msg.edit("**✅ Custom thumbnail set!** All future videos/documents will use it.")


@Client.on_message(filters.command(["delthumb"]))
@access_only
async def del_thumb(client: Client, message):
	if os.path.exists(THUMB_PATH):
		os.remove(THUMB_PATH)
		await client.send_message(message.chat.id, "**🗑 Custom thumbnail removed.**", reply_parameters={"message_id": message.id})
	else:
		await client.send_message(message.chat.id, "__No custom thumbnail is currently set.__", reply_parameters=ReplyParameters(message_id=message.id))
