import os

from flask import request

BLACKLIST_FILE = os.path.abspath("data/blacklist.txt")

# Ensure the directory exists
os.makedirs(os.path.dirname(BLACKLIST_FILE), exist_ok=True)


def load_blacklist():
	if not os.path.exists(BLACKLIST_FILE):
		return set()
	with open(BLACKLIST_FILE, "r") as f:
		return set(line.strip() for line in f if line.strip())


def save_ip_to_blacklist(ip: str) -> None:
	ip = ip.strip()
	if ip != "127.0.0.1":
		with open(BLACKLIST_FILE, "a") as f:
			f.write(f"{ip}\n")


def is_ip_blacklisted(ip: str) -> bool:
	return ip.strip() in load_blacklist()


def get_real_ip():
	# Prefer X-Forwarded-For if it exists (real client IP from proxy)
	if "X-Forwarded-For" in request.headers:
		forwarded_for = request.headers["X-Forwarded-For"]
		# May contain multiple IPs (client, proxy, etc)
		return forwarded_for.split(",")[0].strip()
	return request.remote_addr or "unknown"
