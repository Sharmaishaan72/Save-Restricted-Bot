import pyrogram 
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .. import config 
from ..wrappers.access_only import access_only


USAGE = """**FOR PUBLIC CHATS**

__just send post link(s)__

**FOR PRIVATE CHATS**

__first send invite link of the chat (not needed if the account is already a member of the chat)
then send post link(s)__

**FOR BOT CHATS**

__send link with '/b/', bot's username and message id, you might want to install some unofficial client to get the id__

```
https://t.me/b/botusername/4321
```

**MULTI POSTS**

__send public/private posts link as explained above with format "from - to" to send multiple messages like below__

```
https://t.me/xxxx/1001-1010

https://t.me/c/xxxx/101 - 120
```

__note that space in between doesn't matter__

**ADDING ACCESS & CHANGING STRING SESSION**
__For adding access - use:__
```
/addaccess {user_id}
```

__For changing string session - use:__
```
/string {new_string}
```

__Both of the above no longer need restart - thanks to asyncio__ 

**Custom Thumbnail**
__reply with /setthumb to a picture , all the downloaded media will be sent with that thumbnail , use /delthumb to make it default again__
"""

@Client.on_message(filters.command(["start"]))
@access_only
async def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
	await client.send_message(
		message.chat.id,
		f"__👋 Hi **{message.from_user.mention}**, I am Save Restricted Bot, I can send you restricted content by it's post link__\n\n{USAGE}",
		reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Source Code", url="https://github.com/Sharmaishaan72/Save-Restricted-Bot")]]),
		reply_to_message_id=message.id
	)