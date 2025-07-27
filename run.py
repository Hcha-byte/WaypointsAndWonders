# run.py
import builtins

_original_print = builtins.print  # Save original
# make print flush by default globally
builtins.print = lambda *args, **kwargs: _original_print(*args, **{**kwargs, "flush": True})

from flask import render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app, db, User
from app.models import Post
from app.security.ip_blocklist import get_real_ip

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


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
	app.run(debug=True, port=5000, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
