import json
import os
from datetime import timezone, datetime

from flask import request

from .config import BLACKLIST_FILE

# Ensure the directory exists
os.makedirs(os.path.dirname(BLACKLIST_FILE), exist_ok=True)

import requests


def get_ip_geo(ip):
	response = requests.get(f"https://ipwho.is/{ip}")
	if response.ok:
		data = response.json()
		return {
			"country": data.get("country", "unknown"),
			"city":    data.get("city", "unknown")
		}
	return {"country": "unknown", "city": "unknown"}


def load_blacklist():
	if not os.path.exists(BLACKLIST_FILE):
		return {"blacklisted_ips": {}}
	with open(BLACKLIST_FILE, "r") as f:
		try:
			data = json.load(f)
			
			# Auto-migrate old list format
			if isinstance(data.get("blacklisted_ips"), list):
				data["blacklisted_ips"] = {ip: {"reason": "legacy"} for ip in data["blacklisted_ips"]}
				with open(BLACKLIST_FILE, "w") as wf:
					json.dump(data, wf, indent=2)
			
			if "blacklisted_ips" not in data:
				data["blacklisted_ips"] = {}
			
			return data
		except json.JSONDecodeError:
			return {"blacklisted_ips": {}}


def save_ip_to_blacklist(ip: str, reason="unknown", location="unknown", user_agent="unknown") -> None:
	ip = ip.strip()
	if ip == "127.0.0.1":
		return
	
	data = load_blacklist()
	blacklist = data.get("blacklisted_ips", {})
	
	if ip not in blacklist:
		geo = get_ip_geo(ip)
		
		blacklist[ip] = {
			"reason":     reason,
			"location":   location,
			"user_agent": user_agent,
			"timestamp":  datetime.now(timezone.utc).isoformat() + "Z",
			"country":    geo["country"],
			"city":       geo["city"]
		}
		
		data["blacklisted_ips"] = blacklist
		
		with open(BLACKLIST_FILE, "w") as f:
			json.dump(data, f, indent=2)


def is_ip_blacklisted(ip: str) -> bool:
	return ip.strip() in load_blacklist().get("blacklisted_ips", {})


def get_real_ip():
	# Prefer X-Forwarded-For if it exists (real client IP from proxy)
	if "X-Forwarded-For" in request.headers:
		forwarded_for = request.headers["X-Forwarded-For"]
		# May contain multiple IPs (client, proxy, etc)
		return forwarded_for.split(",")[0].strip()
	return request.remote_addr or "unknown"
