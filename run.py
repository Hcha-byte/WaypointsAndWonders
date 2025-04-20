import os


from flask import render_template, request, redirect, abort
from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# <editor-fold desc="Error handlers">

@app.errorhandler(404)
def page_not_found(e):
	url = request.path
	return render_template('error.html', title='404', functionality=url, message='Page not found'), 404

@app.before_request
def enforce_https():
	if os.getenv("IS_DEV", "TRUE") != "TRUE":
		if not request.is_secure:
			url = request.url.replace("http://", "https://", 1)
			return redirect(url, code=301)

BLOCKED_PATHS = ["wp-", ".php", "/shell", "/filemanager"]
@app.before_request
def block_suspicious():
	if any(bad in request.path.lower() for bad in BLOCKED_PATHS):
		abort(411)
	 
# </editor-fold>

if __name__ == '__main__':
	app.run(debug=True, port=5000, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
