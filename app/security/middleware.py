from flask import redirect, abort, request, current_app
from flask_talisman import Talisman

from app.security.ip_blocklist import get_real_ip, is_ip_blacklisted

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
		"https://code.jquery.com"
	],
	'style-src':       [
		"'self'",
		"'unsafe-inline'",  # ✅ Required for Lightbox2 CSS
		"https://cdn.jsdelivr.net"
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


def register_request_guards(app):
	Talisman(app, force_https=True, content_security_policy=csp)
	
	@app.before_request
	def master_guardian():
		ip = get_real_ip()
		
		# Enforce HTTPS
		if not request.is_secure:
			url = request.url.replace("http://", "https://", 1)
			return redirect(url, code=301)
		
		if is_ip_blacklisted(ip):
			current_app.logger.warning(f"[BLOCKED] IP {ip} is in blacklist.txt")
			abort(410)
		
		user_agent = request.headers.get('User-Agent', '').lower()
		path = request.path
		
		if path not in ["/static/images/favicon.ico", "/static/css/styles.css"]:
			if not user_agent or user_agent.strip() == "":
				abort(403)
			
			if any(bad in path.lower() for bad in BLOCKED_PATHS):
				abort(403)
			
			if any(bad in user_agent for bad in known_bad_bots):
				abort(403)
