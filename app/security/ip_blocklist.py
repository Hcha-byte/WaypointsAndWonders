import json
from datetime import timezone, datetime, timedelta

from flask import request

from .config import BLACKLIST_FILE

# Ensure the directory exists
BLACKLIST_FILE.parent.mkdir(parents=True, exist_ok=True)

import requests


def get_ip_info(ip):
	response = requests.get(f"https://ipwho.is/{ip}")
	if response.ok:
		data = response.json()
		return {
			"country":  data.get("country", "unknown"),
			"city":     data.get("city", "unknown"),
			"asn":      data.get("asn", {}).get("name", "unknown"),
			"isp":      data.get("connection", {}).get("isp", "unknown"),
			"hostname": data.get("connection", {}).get("hostname", "unknown")
		}
	return {
		"country":  "unknown",
		"city":     "unknown",
		"asn":      "unknown",
		"isp":      "unknown",
		"hostname": "unknown"
	}


def load_blacklist():
	if not BLACKLIST_FILE.exists():
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


from dateutil.parser import isoparse  # Much better ISO parser!


def get_recent_blacklist(hours: int = 24):
	all_data = load_blacklist()
	recent_data = {"blacklisted_ips": {}}
	
	now = datetime.now(timezone.utc)
	cutoff = now - timedelta(hours=hours)
	
	for ip, info in all_data.get("blacklisted_ips", {}).items():
		timestamp_str = info.get("timestamp")
		try:
			# Fix malformed timestamp like "+00:00Z"
			if timestamp_str.endswith("Z") and "+" in timestamp_str:
				timestamp_str = timestamp_str.replace("Z", "")  # drop the Z
			
			timestamp = isoparse(timestamp_str)
			if timestamp >= cutoff:
				recent_data["blacklisted_ips"][ip] = info
		except Exception as e:
			print(f"⚠️ Failed to parse timestamp for {ip}: {e}")
			continue
	
	return recent_data


def save_ip_to_blacklist(ip: str, reason="unknown", location="unknown", user_agent="unknown") -> None:
	ip = ip.strip()
	if ip == "127.0.0.1":
		return
	
	data = load_blacklist()
	blacklist = data.get("blacklisted_ips", {})
	
	if ip not in blacklist:
		ip_info = get_ip_info(ip)
		
		blacklist[ip] = {
			"reason":     reason,
			"location":   location,
			"user_agent": user_agent,
			"timestamp":  datetime.now(timezone.utc).isoformat() + "Z",
			"country":    ip_info["country"],
			"city":       ip_info["city"],
			"asn":        ip_info["asn"],
			"isp":        ip_info["isp"],
			"hostname":   ip_info["hostname"]
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
