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
	empty  = bar_length - filled
	bar    = "█" * filled + "░" * empty
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