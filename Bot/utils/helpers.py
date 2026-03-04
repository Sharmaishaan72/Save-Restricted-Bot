# formatting and ui

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


# status writers

import asyncio
import time
import os

from ..client import bot

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
			future = asyncio.run_coroutine_threadsafe(
				bot.edit_message_text(message.chat.id, message.id, text),
				bot.loop
			)
			future.result(timeout=10)
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
			future = asyncio.run_coroutine_threadsafe(
				bot.edit_message_text(message.chat.id, message.id, text),
				bot.loop
			)
			future.result(timeout=10)
		except Exception:
			pass
		time.sleep(10)