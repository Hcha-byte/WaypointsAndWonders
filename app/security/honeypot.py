import os
import random
import time
from datetime import datetime, timezone

from flask import Blueprint, request, render_template_string

from .ip_blocklist import save_ip_to_blacklist, get_real_ip
from ..decoraters import admin_required

LOG_FILE = os.path.join("data", "honeypot.log")

honeypot_bp = Blueprint("honeypot", __name__)


# Use a set for quick membership checks


# Maybe delay the response
def maybe_delay():
	if random.random() < 0.7:  # 70% chance
		delay = random.uniform(0.5, 2.0)
		time.sleep(delay)


# === Constants ===
BLACKLIST_FILE = "data/blacklist.txt"
HONEYPOT_LOG = "data/honeypot.log"
MIDDLEWARE_LOG = "data/middleware.log"


def ensure_log_files():
	for path in [LOG_FILE, BLACKLIST_FILE, HONEYPOT_LOG, MIDDLEWARE_LOG]:
		os.makedirs(os.path.dirname(path), exist_ok=True)
		if not os.path.exists(path):
			with open(path, "w") as f:
				f.write("")


"""
ADMIN_ROUTES = [
	"/_blacklist",
	"/_reset_blacklist",
	"/_honeypot_log",
	"/_clear_honeypot_log",
	"/_middleware_log",
	"/_clear_middleware_log",
	"_ip"
]
"""
"""
HONEYPOT_ROUTES = [
	"/filemanager.php",
	"/admin.php",
	"/shell.php",
	"/database_backup.sql",
	"/.env",
	"/posts.php",
	"/config.php",
	"/wp-login.php",
	"/wp-content",
	"/wp-admin",
	"/wp-includes",
	"/wp-mail"
]
"""


# === Utilities ===
def read_log(path):
	with open(path, "r") as f:
		return f.read().strip().splitlines()


def clear_file(path):
	with open(path, "w") as f:
		f.write("")


# === Routes ===

@honeypot_bp.route("/_blacklist")
@admin_required
def view_trap_hits():
	return {"blacklisted_ips": read_log(BLACKLIST_FILE)}


@honeypot_bp.route("/_reset_blacklist")
@admin_required
def reset_trap_hits():
	clear_file(BLACKLIST_FILE)
	return {
		"blacklisted_ips": [],
		"success":         True
	}


@honeypot_bp.route("/_honeypot_log")
@admin_required
def view_honeypot_log():
	return {"log": read_log(HONEYPOT_LOG)}


@honeypot_bp.route("/_clear_honeypot_log")
@admin_required
def clear_honeypot_log():
	clear_file(HONEYPOT_LOG)
	return {
		"log":     [],
		"success": True
	}


@honeypot_bp.route("/_middleware_log")
@admin_required
def view_middleware_log():
	return {"log": read_log(MIDDLEWARE_LOG)}


@honeypot_bp.route("/_clear_middleware_log")
@admin_required
def clear_middleware_log():
	clear_file(MIDDLEWARE_LOG)
	return {
		"log":     [],
		"success": True
	}


@honeypot_bp.route("/_ip")
@admin_required
def show_ip():
	return {
		"real_ip":     get_real_ip(),
		"remote_addr": request.remote_addr
	}


# Log a trap hit to file
def log_trap_hit_to_file(ip: str, path: str, user_agent: str, tag: str = "Honeypot"):
	timestamp = datetime.now(timezone.utc).isoformat()
	line = f"[{timestamp}][CATEGORY: {tag}] IP: {ip} | PATH: {path} | UA: {user_agent}\n"
	
	os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
	with open(LOG_FILE, "a") as f:
		f.write(line)


# Log a trap hit
def log_trap_hit(tag):
	maybe_delay()
	ip = get_real_ip()
	save_ip_to_blacklist(ip)
	user_agent = request.headers.get('User-Agent', 'unknown')
	path = request.path
	log_trap_hit_to_file(ip, path, user_agent, tag)


# Fake filemanager/login trap
@honeypot_bp.route("/filemanager.php")
@honeypot_bp.route("/admin.php")
@honeypot_bp.route("/shell.php")
def fake_login():
	log_trap_hit("login")
	html = '''
	<!DOCTYPE html><html><head><title>File Manager</title></head>
	<body>
	<h2>File Manager Login</h2>
	<form action="/do_login.php" method="POST">
		<input name="username" placeholder="Username"><br>
		<input name="password" type="password" placeholder="Password"><br>
		<button type="submit">Login</button>
	</form>
	</body></html>
	'''
	return render_template_string(html), 200


# Fake database trap
@honeypot_bp.route("/database_backup.sql")
def fake_db_backup():
	log_trap_hit("db-backup")
	fake_sql = """
	-- Dummy database dump
	CREATE TABLE users (
		id INT PRIMARY KEY,
		username VARCHAR(50),
		password VARCHAR(255)
	);
	INSERT INTO users VALUES (1, 'admin', 'password_hash');
	"""
	return fake_sql, 200, {'Content-Type': 'application/sql'}


# Fake .env trap
@honeypot_bp.route("/.env")
def fake_env():
	log_trap_hit(".env")
	fake_env_content = """
	SECRET_KEY=abc123fake
	DB_PASSWORD=notarealpassword
	AWS_SECRET_KEY=EXAMPLEKEY123
	SENDGRID_API_KEY=SG.fakeapikey
	"""
	return fake_env_content.strip(), 200, {'Content-Type': 'text/plain'}


# Generic .php trap
@honeypot_bp.route("/posts.php")
@honeypot_bp.route("/config.php")
@honeypot_bp.route("/wp-login.php")
def fake_php():
	log_trap_hit("php")
	return "<!-- PHP index file placeholder -->", 200


# WP trap
# non-wildcard routes
@honeypot_bp.route('/wp-content')
@honeypot_bp.route('/wp-admin')
@honeypot_bp.route('/wp-includes')
@honeypot_bp.route('/wp-mail')
# wildcard routes
@honeypot_bp.route('/wp-content<path:rest>')
@honeypot_bp.route('/wp-admin<path:rest>')
@honeypot_bp.route('/wp-includes<path:rest>')
@honeypot_bp.route('/wp-mail<path:rest>')
def fake_wordpress():
	log_trap_hit('wordpress')
	return "<!-- PHP index file placeholder -->", 200
