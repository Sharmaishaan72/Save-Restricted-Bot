# all downloader commands

import os
import time

from pyrogram import Client
from pyrogram import filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied

from .. import config 
from .. import client as mclient 
from ..utils.progress import progress, _progress_state

bot = mclient.bot

def get_message_type(msg):
	try: msg.document.file_id;  return "Document"
	except: pass
	try: msg.video.file_id;     return "Video"
	except: pass
	try: msg.animation.file_id; return "Animation"
	except: pass
	try: msg.sticker.file_id;   return "Sticker"
	except: pass
	try: msg.voice.file_id;     return "Voice"
	except: pass
	try: msg.audio.file_id;     return "Audio"
	except: pass
	try: msg.photo.file_id;     return "Photo"
	except: pass
	try: msg.text;              return "Text"
	except: pass

async def handle_private(message, chatid, msgid):
	acc = mclient.acc 	
	msg = await acc.get_messages(chatid, msgid)
	msg_type = get_message_type(msg)

	if msg_type == "Text":
		try:
			await bot.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
		except:
			text_to_send = msg.text if msg.text else "** **"
			entities_to_send = msg.entities if msg.entities else None
			await bot.send_message(message.chat.id, text_to_send, entities=entities_to_send, reply_to_message_id=message.id)
		return

	smsg = await bot.send_message(message.chat.id, '__Downloading__\n\n`Starting...`', reply_to_message_id=message.id)

	file = await acc.download_media(
		msg,
		progress=progress,
		progress_args=[message, smsg, "down"]
	)

	_progress_state.pop(f"{message.id}down", None)

	await smsg.edit_text('__Uploading__\n\n`Starting...`')

	caption          = msg.caption if msg.caption else ""
	caption_entities = msg.caption_entities if msg.caption_entities else None

	if msg_type == "Document":
		try: thumb = await acc.download_media(msg.document.thumbs[0].file_id)
		except: thumb = None
		await bot.send_document(message.chat.id, file, thumb=thumb, caption=caption, caption_entities=caption_entities,
		                  reply_to_message_id=message.id, progress=progress, progress_args=[message, smsg, "up"])
		if thumb: os.remove(thumb)

	elif msg_type == "Video":
		try: thumb = await acc.download_media(msg.video.thumbs[0].file_id)
		except: thumb = None
		await bot.send_video(message.chat.id, file, duration=msg.video.duration, width=msg.video.width,
		               height=msg.video.height, thumb=thumb, caption=caption, caption_entities=caption_entities,
		               reply_to_message_id=message.id, progress=progress, progress_args=[message, smsg, "up"])
		if thumb: os.remove(thumb)

	elif msg_type == "Animation":
		await bot.send_animation(message.chat.id, file, caption=caption, caption_entities=caption_entities,
		                   reply_to_message_id=message.id)

	elif msg_type == "Sticker":
		await bot.send_sticker(message.chat.id, file, reply_to_message_id=message.id)

	elif msg_type == "Voice":
		try: thumb = await acc.download_media(msg.voice.thumbs[0].file_id) if hasattr(msg.voice, 'thumbs') and msg.voice.thumbs else None
		except: thumb = None
		await bot.send_voice(message.chat.id, file, caption=caption, thumb=thumb, caption_entities=caption_entities,
		               reply_to_message_id=message.id, progress=progress, progress_args=[message, smsg, "up"])
		if thumb: os.remove(thumb)

	elif msg_type == "Audio":
		try: thumb = await acc.download_media(msg.audio.thumbs[0].file_id)
		except: thumb = None
		await bot.send_audio(message.chat.id, file, caption=caption, caption_entities=caption_entities,
		               reply_to_message_id=message.id, progress=progress, progress_args=[message, smsg, "up"])
		if thumb: os.remove(thumb)

	elif msg_type == "Photo":
		await bot.send_photo(message.chat.id, file, caption=caption, caption_entities=caption_entities,
		               reply_to_message_id=message.id)

	os.remove(file)

	_progress_state.pop(f"{message.id}up", None)

	await bot.delete_messages(message.chat.id, [smsg.id])



@Client.on_message(filters.regex(r"^(?:https?://)?t\.me/.+$") & filters.user(config.config.owner_ids))
async def save(client: Client, message):
	print(message.text)
	acc = mclient.acc 
	# joining chats
	if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:
		if acc is None:
			await client.send_message(message.chat.id, "**String Session is not Set**", reply_to_message_id=message.id)
			return
		try:
			try: await acc.join_chat(message.text)
			except Exception as e:
				await client.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)
				return
			await client.send_message(message.chat.id, "**Chat Joined**", reply_to_message_id=message.id)
		except UserAlreadyParticipant:
			await client.send_message(message.chat.id, "**Chat already Joined**", reply_to_message_id=message.id)
		except InviteHashExpired:
			await client.send_message(message.chat.id, "**Invalid Link**", reply_to_message_id=message.id)

	# getting message
	elif "https://t.me/" in message.text:
		datas = message.text.split("/")
		temp = datas[-1].replace("?single", "").split("-")
		fromID = int(temp[0].strip())
		try: toID = int(temp[1].strip())
		except: toID = fromID

		for msgid in range(fromID, toID + 1):

			# private
			if "https://t.me/c/" in message.text:
				chatid = int("-100" + datas[4])
				if acc is None:
					await client.send_message(message.chat.id, "**String Session is not Set**", reply_to_message_id=message.id)
					return
				try: await handle_private(message, chatid, msgid)
				except Exception as e: await client.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

			# bot
			elif "https://t.me/b/" in message.text:
				username = datas[4]
				if acc is None:
					await client.send_message(message.chat.id, "**String Session is not Set**", reply_to_message_id=message.id)
					return
				try: await handle_private(message, username, msgid)
				except Exception as e: await client.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

			# public
			else:
				username = datas[3]
				try: msg = await client.get_messages(username, msgid)
				except UsernameNotOccupied:
					await client.send_message(message.chat.id, "**The username is not occupied by anyone**", reply_to_message_id=message.id)
					return
				try: await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
				except:
					if acc is None:
						await client.send_message(message.chat.id, "**String Session is not Set**", reply_to_message_id=message.id)
						return
					try: await handle_private(message, username, msgid)
					except Exception as e: await client.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

			time.sleep(3)