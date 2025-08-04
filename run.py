# run.py
import builtins

_original_print = builtins.print  # Save original
# make print flush by default globally
builtins.print = lambda *args, **kwargs: _original_print(*args, **{**kwargs, "flush": True})
import logging
import sys
from app.logging.log_colorizer import ColorFormatter

formatter = ColorFormatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S %Z")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

logging.basicConfig(
	level=logging.INFO,
	handlers=[handler],
	force=True  # override all handlers
)

# Optional: individually set other loggers
for name in ["hypercorn.access", "werkzeug", "hypercorn.error"]:
	logger = logging.getLogger(name)
	logger.handlers.clear()
	logger.addHandler(handler)
	logger.setLevel(logging.INFO)

from flask import render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app, db, User
from app.models import Post
from app.security.ip_blocklist import get_real_ip

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config


async def main():
	config = Config()
	config.bind = ["0.0.0.0:5000"]
	if not app.config["IS_ON_RAILWAY"]:
		config.certfile = "cert.pem"
		config.keyfile = "key.pem"
	config.accesslog = "-"
	config.access_log_format = ' -- %(r)s %(s)s'
	import pathlib
	
	config.logconfig = str(pathlib.Path("hypercorn_log_config.ini"))
	config.loglevel = "info"
	# Add any other Hypercorn config options here
	
	await serve(app, config, mode="wsgi")


# <editor-fold desc="Error handlers">


@app.errorhandler(404)
def page_not_found(e):
	url = request.path
	return render_template('error.html', title='404', functionality=url, message='Page not found'), 404


@app.errorhandler(403)
def forbidden(e):
	return render_template('error.html', title='403', functionality=request.path,
	                       message='Forbidden dues to suspicious client activity'), 403


@app.errorhandler(410)
def blacklisted(e):
	return render_template('error.html', title='410', functionality=get_real_ip(),
	                       message='Your IP has been blacklisted, please appel to an admin for more information.'), 410


@app.errorhandler(500)
def internal_server_error(e):
	return render_template('error.html', title='500', functionality="There was an internal server error",
	                       message=e), 500


@app.shell_context_processor
def make_shell_context():
	return {
		'db':   db,
		'User': User,
		'Post': Post
	}


# </editor-fold>

if __name__ == '__main__':
	try:
		asyncio.run(main())
	except Exception as e:
		logging.getLogger().exception("🚨 Server failed to start")
		raise
