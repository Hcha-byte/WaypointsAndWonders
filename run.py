from flask import render_template, redirect, abort, request
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app, db, User
from app.models import Post

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


# <editor-fold desc="Error handlers">


@app.errorhandler(404)
def page_not_found(e):
	url = request.path
	return render_template('error.html', title='404', functionality=url, message='Page not found'), 404


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

Talisman(app, force_https=True, content_security_policy=csp)


@app.before_request
def enforce_https():
	if not request.is_secure:
		url = request.url.replace("http://", "https://", 1)
		return redirect(url, code=301)
	return None


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


@app.before_request
def block_suspicious():
	user_agent = request.headers.get('User-Agent', '').lower()
	
	if (request.path != "/static/images/favicon.ico") and (request.path != "/static/css/styles.css"):
		
		if not user_agent:
			abort(403)
		
		if any(bad in request.path.lower() for bad in BLOCKED_PATHS):
			abort(403)
		
		if user_agent.strip() == "":
			abort(403)
		
		if any(bad in user_agent for bad in known_bad_bots):
			abort(403)


@app.errorhandler(403)
def forbidden(e):
	return render_template('error.html', title='403', functionality=request.path,
	                       message='Forbidden dues to suspicious client activity'), 403


@app.shell_context_processor
def make_shell_context():
	return {
		'db':   db,
		'User': User,
		'Post': Post
	}


# </editor-fold>

if __name__ == '__main__':
	app.run(debug=True, port=5000, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
