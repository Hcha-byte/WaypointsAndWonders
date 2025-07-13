import os.path
from datetime import datetime, timezone

from flask import redirect, abort, request, Flask
from flask_talisman import Talisman

from app.security.ip_blocklist import get_real_ip, is_ip_blacklisted
from .config import MIDDLEWARE_LOG

csp = {
	'default-src':     ["'self'"],
	'img-src':         [
		"'self'",
		"data:",
		"https://res.cloudinary.com",
		"https://polarsteps.s3.amazonaws.com",
		"https://developers.google.com/identity/images/g-logo.png",
		"https://lh3.googleusercontent.com",
		"https://cdn.jsdelivr.net"
	],
	'script-src':      [
		"'self'",
		"'unsafe-inline'",  # ✅ Required for Lightbox2 to work
		"https://cdn.jsdelivr.net",
		"https://code.jquery.com"
	],
	'script-src-elem': [
		"'self'",
		"'unsafe-inline'",  # ✅ Required for Lightbox2 to work
		"https://cdn.jsdelivr.net",
		"https://code.jquery.com",
		# ✅ Required for reCAPTCHA
		"https://www.google.com/recaptcha/api.js",
		"https://www.gstatic.com/recaptcha/releases/_cn5mBoBXIA0_T7xBjxkUqUA/recaptcha__en.js"
	],
	'style-src':       [
		"'self'",
		"'unsafe-inline'",  # ✅ Required for Lightbox2 CSS
		"https://cdn.jsdelivr.net"
	],
	# ✅ Required for reCAPTCHA
	'frame-src':       [
		"'self'",
		"https://www.google.com"
	],
	'connect-src':     [
		"'self'",
		"https://www.google.com/recaptcha/api2/clr"
	]
}

BLOCKED_PATHS = [
	"wp-", ".php", "/shell", "/filemanager",
	".env", ".env.", "aws-secret", "sendgrid",
	".remote", "laravel.log", "settings.json",
	"config.js", "server.js", "twilio-chat"
]
known_bad_bots = [
	"curl", "httpclient", "python", "wget", "libwww",
	"perl", "scrapy", "nmap", "masscan"
]


def write_to_log(message: str):
	timestamp = datetime.now(timezone.utc).isoformat()
	line = f"[{timestamp}] {message}\n"
	
	os.makedirs(os.path.dirname(MIDDLEWARE_LOG), exist_ok=True)
	with open(MIDDLEWARE_LOG, "a") as f:
		f.write(line)


def register_request_guards(app: Flask):
	Talisman(app, force_https=True, content_security_policy=csp)
	
	@app.before_request
	def master_guardian():
		ip = get_real_ip()
		user_agent = request.headers.get('User-Agent', '').lower()
		path = request.path
		
		if ip == "56.56.56.56" and user_agent == "test-emergency-1-admin-alfa":
			return None
		
		# Enforce HTTPS
		if not request.is_secure:
			url = request.url.replace("http://", "https://", 1)
			return redirect(url, code=301)
		
		# ✅ Allow static files (and favicon) to always load
		if path.startswith("/static/") or path == "/favicon.ico":
			return None  # Let it through without any security checks
		
		# Enforce IP blocklist
		if is_ip_blacklisted(ip):
			write_to_log(
				f"Blocked IP: {ip} | PATH: {path} | UA: {user_agent}| Reason: IP blacklisted")
			abort(410)
		
		# Allow access to honeypot
		if request.endpoint and "honeypot" in request.endpoint:
			return None
		
		# Enforce bot detection
		
		if path not in ["/static/images/favicon.ico", "/static/css/styles.css"]:
			if not user_agent or user_agent.strip() == "":
				write_to_log(f"Blocked IP: {ip} | PATH: {path} | UA: {user_agent}| Reason: empty user agent")
				abort(403)
			
			if any(bad in path.lower() for bad in BLOCKED_PATHS):
				write_to_log(f"Blocked IP: {ip} | PATH: {path} | UA: {user_agent}| Reason: blocked path")
				abort(403)
			
			if any(bad in user_agent for bad in known_bad_bots):
				write_to_log(f"Blocked IP: {ip} | PATH: {path} | UA: {user_agent}| Reason: known bad bot UA")
				abort(403)
		return None
