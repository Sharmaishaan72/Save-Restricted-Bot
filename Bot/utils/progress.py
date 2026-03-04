# ── progress callback (fully async) ───────────────────────────────────────────

import time

from .helpers import human_size, make_progress_bar, format_eta

# Tracks per-transfer state: speed calculation + last Telegram edit time
_progress_state: dict = {}

async def progress(current: int, total: int, message, smsg, transfer_type: str):
	"""
	Async progress callback for Pyrogram download/upload.
	Edits `smsg` directly with a live progress bar.

	Rate-limited to one Telegram edit every 5 seconds to avoid flood errors.

	progress_args should be: [message, smsg, "down"/"up"]
	"""
	key = f"{message.id}{transfer_type}"
	now = time.time()

	if key not in _progress_state:
		_progress_state[key] = {
			"start_time":   now,
			"last_time":    now,
			"last_current": current,
			"speed":        0.0,
			"last_edit":    0.0,
		}

	state   = _progress_state[key]
	elapsed = now - state["last_time"]

	# Update rolling speed once per second
	if elapsed >= 1.0:
		delta          = current - state["last_current"]
		state["speed"] = delta / elapsed if elapsed > 0 else 0.0
		state["last_time"]    = now
		state["last_current"] = current

	# Rate-limit Telegram edits to once every 5 seconds
	if now - state["last_edit"] < 5:
		return

	speed = state["speed"]
	pct   = current * 100 / total if total else 0
	eta   = (total - current) / speed if speed > 0 else -1.0
	label = "__Downloading__" if transfer_type == "down" else "__Uploading__"
	bar   = make_progress_bar(pct)

	text = (
		f"{label}\n\n"
		f"{bar}\n"
		f"`{human_size(current)} / {human_size(total)}`\n"
		f"⚡ Speed: `{human_size(speed)}/s`\n"
		f"⏳ ETA:   `{format_eta(eta)}`"
	)

	try:
		await smsg.edit_text(text)
		state["last_edit"] = now
	except Exception:
		pass
