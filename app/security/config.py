import os


def get_data_path(filename):
	# Use /data if it exists (Railway volume), otherwise fallback to local folder
	base_dir = "/data" if os.path.exists("/data") else "data"
	os.makedirs(base_dir, exist_ok=True)
	return os.path.join(base_dir, filename)


# Use this everywhere
BLACKLIST_FILE = get_data_path("blacklist.json")
HONEYPOT_LOG = get_data_path("honeypot.log")
MIDDLEWARE_LOG = get_data_path("middleware.log")
