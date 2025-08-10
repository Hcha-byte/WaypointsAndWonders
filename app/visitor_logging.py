# app/visitor_logging.py

from flask import request, session, current_app, Flask


def register_single_visit_logger(app: Flask):
	@app.before_request
	def log_single_visit():
		if session.get("visited"):
			return  # Already logged this session
		
		# Ignore non-page requests and heartbeat
		ua = request.user_agent.string
		path = request.path
		if path.startswith(('/static', '/favicon')) or path == "/heartbeat":
			return
		if not ua:  # Handles None or empty string
			return
		
		ua_under = ua.lower()
		
		# Blacklist: reject immediately if bot-like
		bot_signatures = [
			'bot',
			'spider',
			'crawler',
			'slurp',
			'archive',
			'headless',
			'phantom',
			'compatible;',
			'googlebot'
		]
		if any(sig in ua_under for sig in bot_signatures):
			return
		
		# Whitelist: allow only if known browser
		browser_signatures = [
			'chrome',
			'firefox',
			'safari',  # Includes mobile Safari
			'edg',  # Microsoft Edge
			'opera',
			'opr/',  # Opera
			'vivaldi',
			'brave'
		]
		if not any(sig in ua_under for sig in browser_signatures):
			return
		
		ip = request.headers.get("X-Forwarded-For", request.remote_addr)
		
		current_app.logger.info(f"Visitor: IP={ip} | UA={ua}")
		
		session["visited"] = True
