import os
import random
import time

from flask import Blueprint, request, render_template_string, current_app

from .ip_blocklist import load_blacklist, save_ip_to_blacklist, get_real_ip
from ..decoraters import admin_required

LOG_FILE = os.path.join("data", "honeypot.log")

honeypot_bp = Blueprint("honeypot", __name__)
# Use a set for quick membership checks


trap_hits = []


def maybe_delay():
	if random.random() < 0.7:  # 70% chance
		delay = random.uniform(0.5, 2.0)
		time.sleep(delay)


@honeypot_bp.route("/_trap-log")
@admin_required
def view_trap_hits():
	return {"blacklisted_ips": list(load_blacklist())}


@honeypot_bp.route("/_ip")
def show_ip():
	return {"real_ip": get_real_ip(), "remote_addr": request.remote_addr}


def log_trap_hit(tag):
	maybe_delay()
	ip = get_real_ip()
	save_ip_to_blacklist(ip)
	user_agent = request.headers.get('User-Agent', 'unknown')
	path = request.path
	trap_hits.append((tag, ip, user_agent, path))
	current_app.logger.warning(f"[HONEYPOT:{tag}] {path} hit by {ip} UA: {user_agent}")


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


@honeypot_bp.route('/posts.php')
def fake_posts():
	log_trap_hit('posts')
	return "<!-- PHP index file placeholder -->", 200
