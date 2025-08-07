# app/visitor_logging.py
from datetime import datetime

import pytz
from flask import request, session, current_app, Flask


def register_single_visit_logger(app: Flask):
	@app.before_request
	def log_single_visit():
		if session.get("visited"):
			return  # Already logged this session
		
		# Ignore non-page requests and heartbeat
		path = request.path
		if path.startswith(('/static', '/favicon')) or path == "/heartbeat":
			return
		
		ip = request.headers.get("X-Forwarded-For", request.remote_addr)
		ua = request.user_agent.string
		timestamp = datetime.now(pytz.timezone("America/Denver")).strftime("%Y-%m-%d %H:%M:%S")
		
		current_app.logger.info(f"[{timestamp}] New visitor: IP={ip} | UA={ua}")
		
		session["visited"] = True
