import json
from pathlib import Path


def load_blacklist(path: str = "data/blacklist.json"):
	if not Path(path).exists():
		return {}
	with open(path, "r") as f:
		return json.load(f).get("blacklisted_ips", {})
