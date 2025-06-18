from functools import wraps

from flask import flash, redirect, url_for, request
from flask_login import current_user, login_required


def is_bot():
	user_agent = request.headers.get('User-Agent', '').lower()
	known_bots = [
		"googlebot", "bingbot", "slurp", "duckduckbot",
		"baiduspider", "yandexbot", "sogou", "exabot"
	]
	return any(bot in user_agent for bot in known_bots)


def admin_required(f):
	@wraps(f)
	@login_required
	def decorated_function(*args, **kwargs):
		if not current_user.is_authenticated or not current_user.is_admin:
			flash("Access denied: Admins only", "danger")
			return redirect(url_for("main.home"))  # Redirect non-admin users
		return f(*args, **kwargs)
	
	return decorated_function


def login_bot(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if current_user.is_authenticated:
			return f(*args, **kwargs)
		elif is_bot():
			return f(*args, **kwargs)
		else:
			# Preserve the original requested URL in 'next' parameter
			return redirect(url_for("auth.login", next=request.path))
	
	return decorated_function
