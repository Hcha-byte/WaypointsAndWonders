from pathlib import Path


def get_data_path(filename: str) -> Path:
	# Use /data if it exists (Railway volume), otherwise fallback to local folder
	base_dir = Path("/data") if Path("/data").exists() else Path("data")
	base_dir.mkdir(parents=True, exist_ok=True)
	return base_dir / filename


# Use these everywhere
BLACKLIST_FILE: Path = get_data_path("blacklist.json")
RECENT_BLACKLIST_FILE: Path = get_data_path("recent_blacklist.json")
HONEYPOT_LOG: Path = get_data_path("honeypot.log")
MIDDLEWARE_LOG: Path = get_data_path("middleware.log")
SUMMARY_LATEST: Path = get_data_path("summary_latest.html")
