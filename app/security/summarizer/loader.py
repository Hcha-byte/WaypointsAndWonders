import json
from pathlib import Path

from ..config import BLACKLIST_FILE


def load_blacklist(path: Path = BLACKLIST_FILE):
	if not Path(path).exists():
		return {}
	with path.open("r") as f:
		return json.load(f).get("blacklisted_ips", {})
