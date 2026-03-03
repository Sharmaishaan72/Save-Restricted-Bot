# ── progress callback ─────────────────────────────────────────────────────────

import time

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
