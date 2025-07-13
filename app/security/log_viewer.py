import json

from flask import Blueprint

from .config import HONEYPOT_LOG, MIDDLEWARE_LOG, BLACKLIST_FILE
from .ip_blocklist import get_real_ip, get_ip_geo
from ..decoraters import admin_required

log_viewer_bp = Blueprint("log_viewer", __name__)


# === Utilities ===
def read_log(path):
	with open(path, "r") as f:
		return f.read().strip().splitlines()


def clear_file(path):
	with open(path, "w") as f:
		f.write("")


# === Routes ===

@log_viewer_bp.route("/_blacklist")
@admin_required
def view_trap_hits():
	try:
		with open(BLACKLIST_FILE) as f:
			data = json.load(f)
			return {"blacklisted_ips": data.get("blacklisted_ips", {})}
	except (FileNotFoundError, json.JSONDecodeError):
		return {"blacklisted_ips": {}, "error": "Could not read blacklist.json"}, 500


@log_viewer_bp.route("/_reset_blacklist")
@admin_required
def reset_trap_hits():
	with open(BLACKLIST_FILE, "w") as f:
		json.dump({"blacklisted_ips": {}}, f, indent=2)
	return {
		"blacklisted_ips": {},
		"success":         True
	}


@log_viewer_bp.route("/_honeypot_log")
@admin_required
def view_honeypot_log():
	return {"log": read_log(HONEYPOT_LOG)}


@log_viewer_bp.route("/_clear_honeypot_log")
@admin_required
def clear_honeypot_log():
	clear_file(HONEYPOT_LOG)
	return {
		"log":     read_log(HONEYPOT_LOG),
		"success": True
	}


@log_viewer_bp.route("/_middleware_log")
@admin_required
def view_middleware_log():
	return {"log": read_log(MIDDLEWARE_LOG)}


@log_viewer_bp.route("/_clear_middleware_log")
@admin_required
def clear_middleware_log():
	clear_file(MIDDLEWARE_LOG)
	return {
		"log":     read_log(MIDDLEWARE_LOG),
		"success": True
	}


@log_viewer_bp.route("/_ip")
@admin_required
def show_ip():
	ip = get_real_ip()
	geo = get_ip_geo(ip)
	city = geo.get("city", "unknown")
	country = geo.get("country", "unknown")
	return {
		"ip":      ip,
		"city":    city,
		"country": country
	}
