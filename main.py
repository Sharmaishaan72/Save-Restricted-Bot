import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import time
import os
import threading
import json

# Fix for PEER_ID_INVALID error - Update MIN_CHANNEL_ID and MIN_CHAT_ID
import pyrogram.utils as utils
utils.MIN_CHANNEL_ID = -1007852516352
utils.MIN_CHAT_ID = -999999999999

with open('config.json', 'r') as f: DATA = json.load(f)
def getenv(var): return os.environ.get(var) or DATA.get(var, None)

bot_token = getenv("TOKEN") 
api_hash = getenv("HASH") 
api_id = getenv("ID")
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

ss = getenv("STRING")
if ss is not None:
	acc = Client("myacc" ,api_id=api_id, api_hash=api_hash, session_string=ss)
	acc.start()
else: acc = None


# ── helpers ──────────────────────────────────────────────────────────────────

def human_size(num: float) -> str:
	"""Convert bytes to a human-readable string."""
	for unit in ("B", "KB", "MB", "GB"):
		if abs(num) < 1024.0:
			return f"{num:.1f} {unit}"
		num /= 1024.0
	return f"{num:.1f} TB"


def make_progress_bar(percentage: float, bar_length: int = 10) -> str:
	filled = int(bar_length * percentage / 100)
	empty = bar_length - filled
	bar = "█" * filled + "░" * empty
	return f"[{bar}] {percentage:.1f}%"


def format_eta(seconds: float) -> str:
	"""Format seconds into a human-readable ETA string."""
	if seconds < 0 or seconds > 86400:
		return "??:??:??"
	h = int(seconds // 3600)
	m = int((seconds % 3600) // 60)
	s = int(seconds % 60)
	if h:
		return f"{h:02d}:{m:02d}:{s:02d}"
	return f"{m:02d}:{s:02d}"


# ── status writers ────────────────────────────────────────────────────────────

def downstatus(statusfile: str, message):
	"""Background thread: reads the status file and updates the Telegram message."""
	while not os.path.exists(statusfile):
		time.sleep(0.5)

	time.sleep(3)
	while os.path.exists(statusfile):
		try:
			with open(statusfile, "r") as f:
				txt = f.read().strip()
			# Format: "percentage|current|total|speed|eta"
			parts = txt.split("|")
			pct   = float(parts[0])
			curr  = int(parts[1])
			total = int(parts[2])
			speed = float(parts[3])   # bytes/sec
			eta   = float(parts[4])   # seconds

			bar = make_progress_bar(pct)
			text = (
				f"__Downloading__\n\n"
				f"{bar}\n"
				f"`{human_size(curr)} / {human_size(total)}`\n"
				f"⚡ Speed: `{human_size(speed)}/s`\n"
				f"⏳ ETA:   `{format_eta(eta)}`"
			)
			bot.edit_message_text(message.chat.id, message.id, text)
		except Exception:
			pass
		time.sleep(10)


def upstatus(statusfile: str, message):
	"""Background thread: reads the status file and updates the Telegram message."""
	while not os.path.exists(statusfile):
		time.sleep(0.5)

	time.sleep(3)
	while os.path.exists(statusfile):
		try:
			with open(statusfile, "r") as f:
				txt = f.read().strip()
			parts = txt.split("|")
			pct   = float(parts[0])
			curr  = int(parts[1])
			total = int(parts[2])
			speed = float(parts[3])
			eta   = float(parts[4])

			bar = make_progress_bar(pct)
			text = (
				f"__Uploading__\n\n"
				f"{bar}\n"
				f"`{human_size(curr)} / {human_size(total)}`\n"
				f"⚡ Speed: `{human_size(speed)}/s`\n"
				f"⏳ ETA:   `{format_eta(eta)}`"
			)
			bot.edit_message_text(message.chat.id, message.id, text)
		except Exception:
			pass
		time.sleep(10)


# ── progress callback ─────────────────────────────────────────────────────────

# We keep a small dict to track start-time & last-sample per transfer ID so we
# can compute a rolling speed rather than an instantaneous one.
_progress_state: dict = {}

def progress(current: int, total: int, message, transfer_type: str):
	"""
	Called by Pyrogram on every chunk.  Writes a pipe-separated status file:
	  percentage|current|total|speed_bytes_per_sec|eta_seconds
	"""
	key = f"{message.id}{transfer_type}"
	now = time.time()

	if key not in _progress_state or current < _progress_state[key]["last_current"]:
		# New transfer or restart
		_progress_state[key] = {
			"start_time":   now,
			"last_time":    now,
			"last_current": current,
			"speed":        0.0,
		}

	state = _progress_state[key]
	elapsed = now - state["last_time"]

	if elapsed >= 1.0:  # update speed every second
		delta_bytes = current - state["last_current"]
		speed = delta_bytes / elapsed if elapsed > 0 else 0.0
		state["speed"]        = speed
		state["last_time"]    = now
		state["last_current"] = current
	else:
		speed = state["speed"]

	pct = current * 100 / total if total else 0
	remaining = total - current
	eta = remaining / speed if speed > 0 else -1.0

	filename = f"{key}status.txt"
	with open(filename, "w") as f:
		f.write(f"{pct:.1f}|{current}|{total}|{speed:.1f}|{eta:.1f}")


# ── owner / admin config ──────────────────────────────────────────────────────

OWNER_ID = 2055774115  # Your Telegram user ID


# ── commands ──────────────────────────────────────────────────────────────────

@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
	bot.send_message(
		message.chat.id,
		f"__👋 Hi **{message.from_user.mention}**, I am Save Restricted Bot, I can send you restricted content by it's post link__\n\n{USAGE}",
		reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Source Code", url="https://github.com/bipinkrish/Save-Restricted-Bot")]]),
		reply_to_message_id=message.id
	)


@bot.on_message(filters.command(["token"]) & filters.user(OWNER_ID))
def set_token(client, message):
	if len(message.command) < 2:
		bot.send_message(message.chat.id, "__Usage__: `/token NEW_BOT_TOKEN`", reply_to_message_id=message.id)
		return
	DATA["TOKEN"] = message.command[1].strip()
	with open("config.json", "w") as f:
		json.dump(DATA, f, indent=4)
	bot.send_message(message.chat.id, "**TOKEN updated. Please restart the bot.**", reply_to_message_id=message.id)


@bot.on_message(filters.command(["string"]) & filters.user(OWNER_ID))
def set_string_session(client, message):
	if len(message.command) < 2:
		bot.send_message(message.chat.id, "__Usage__: `/string NEW_STRING_SESSION`", reply_to_message_id=message.id)
		return
	DATA["STRING"] = message.command[1].strip()
	with open("config.json", "w") as f:
		json.dump(DATA, f, indent=4)
	bot.send_message(message.chat.id, "**STRING session updated. Please restart the bot.**", reply_to_message_id=message.id)


# ── main message handler ──────────────────────────────────────────────────────

@bot.on_message(filters.text)
def save(client, message):
	print(message.text)

	# joining chats
	if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:
		if acc is None:
			bot.send_message(message.chat.id, "**String Session is not Set**", reply_to_message_id=message.id)
			return
		try:
			try: acc.join_chat(message.text)
			except Exception as e:
				bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)
				return
			bot.send_message(message.chat.id, "**Chat Joined**", reply_to_message_id=message.id)
		except UserAlreadyParticipant:
			bot.send_message(message.chat.id, "**Chat already Joined**", reply_to_message_id=message.id)
		except InviteHashExpired:
			bot.send_message(message.chat.id, "**Invalid Link**", reply_to_message_id=message.id)

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
					bot.send_message(message.chat.id, "**String Session is not Set**", reply_to_message_id=message.id)
					return
				try: handle_private(message, chatid, msgid)
				except Exception as e: bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

			# bot
			elif "https://t.me/b/" in message.text:
				username = datas[4]
				if acc is None:
					bot.send_message(message.chat.id, "**String Session is not Set**", reply_to_message_id=message.id)
					return
				try: handle_private(message, username, msgid)
				except Exception as e: bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

			# public
			else:
				username = datas[3]
				try: msg = bot.get_messages(username, msgid)
				except UsernameNotOccupied:
					bot.send_message(message.chat.id, "**The username is not occupied by anyone**", reply_to_message_id=message.id)
					return
				try: bot.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
				except:
					if acc is None:
						bot.send_message(message.chat.id, "**String Session is not Set**", reply_to_message_id=message.id)
						return
					try: handle_private(message, username, msgid)
					except Exception as e: bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

			time.sleep(3)


# ── private handler ───────────────────────────────────────────────────────────

def handle_private(message, chatid, msgid):
	msg = acc.get_messages(chatid, msgid)
	msg_type = get_message_type(msg)

	if msg_type == "Text":
		try:
			bot.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
		except:
			text_to_send = msg.text if msg.text else "** **"
			entities_to_send = msg.entities if msg.entities else None
			bot.send_message(message.chat.id, text_to_send, entities=entities_to_send, reply_to_message_id=message.id)
		return

	smsg = bot.send_message(message.chat.id, '__Downloading__\n\n`Starting...`', reply_to_message_id=message.id)

	dosta = threading.Thread(
		target=lambda: downstatus(f'{message.id}downstatus.txt', smsg),
		daemon=True
	)
	dosta.start()

	file = acc.download_media(
		msg,
		progress=progress,
		progress_args=[message, "down"]
	)

	# Clean up download status
	down_status_file = f'{message.id}downstatus.txt'
	if os.path.exists(down_status_file):
		os.remove(down_status_file)
	_progress_state.pop(f"{message.id}down", None)

	bot.edit_message_text(smsg.chat.id, smsg.id, '__Uploading__\n\n`Starting...`')

	upsta = threading.Thread(
		target=lambda: upstatus(f'{message.id}upstatus.txt', smsg),
		daemon=True
	)
	upsta.start()

	caption          = msg.caption if msg.caption else ""
	caption_entities = msg.caption_entities if msg.caption_entities else None

	if msg_type == "Document":
		try: thumb = acc.download_media(msg.document.thumbs[0].file_id)
		except: thumb = None
		bot.send_document(message.chat.id, file, thumb=thumb, caption=caption, caption_entities=caption_entities,
		                  reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
		if thumb: os.remove(thumb)

	elif msg_type == "Video":
		try: thumb = acc.download_media(msg.video.thumbs[0].file_id)
		except: thumb = None
		bot.send_video(message.chat.id, file, duration=msg.video.duration, width=msg.video.width,
		               height=msg.video.height, thumb=thumb, caption=caption, caption_entities=caption_entities,
		               reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
		if thumb: os.remove(thumb)

	elif msg_type == "Animation":
		bot.send_animation(message.chat.id, file, caption=caption, caption_entities=caption_entities,
		                   reply_to_message_id=message.id)

	elif msg_type == "Sticker":
		bot.send_sticker(message.chat.id, file, reply_to_message_id=message.id)

	elif msg_type == "Voice":
		try: thumb = acc.download_media(msg.voice.thumbs[0].file_id) if hasattr(msg.voice, 'thumbs') and msg.voice.thumbs else None
		except: thumb = None
		bot.send_voice(message.chat.id, file, caption=caption, thumb=thumb, caption_entities=caption_entities,
		               reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
		if thumb: os.remove(thumb)

	elif msg_type == "Audio":
		try: thumb = acc.download_media(msg.audio.thumbs[0].file_id)
		except: thumb = None
		bot.send_audio(message.chat.id, file, caption=caption, caption_entities=caption_entities,
		               reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
		if thumb: os.remove(thumb)

	elif msg_type == "Photo":
		bot.send_photo(message.chat.id, file, caption=caption, caption_entities=caption_entities,
		               reply_to_message_id=message.id)

	os.remove(file)

	up_status_file = f'{message.id}upstatus.txt'
	if os.path.exists(up_status_file):
		os.remove(up_status_file)
	_progress_state.pop(f"{message.id}up", None)

	bot.delete_messages(message.chat.id, [smsg.id])


# ── message type detector ─────────────────────────────────────────────────────

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


USAGE = """**FOR PUBLIC CHATS**

__just send post/s link__

**FOR PRIVATE CHATS**

__first send invite link of the chat (unnecessary if the account of string session already member of the chat)
then send post/s link__

**FOR BOT CHATS**

__send link with '/b/', bot's username and message id, you might want to install some unofficial client to get the id like below__

```
https://t.me/b/botusername/4321
```

**MULTI POSTS**

__send public/private posts link as explained above with formate "from - to" to send multiple messages like below__

```
https://t.me/xxxx/1001-1010

https://t.me/c/xxxx/101 - 120
```

__note that space in between doesn't matter__
"""


# infinity polling
bot.run()
