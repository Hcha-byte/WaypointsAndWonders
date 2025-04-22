from flask import render_template, redirect, abort, request, url_for
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
	if not request.is_secure:
		url = request.url.replace("http://", "https://", 1)
		return redirect(url, code=301)

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
	
	if not user_agent:
		abort(403)
		
	if any(bad in request.path.lower() for bad in BLOCKED_PATHS):
		abort(403)
		
	if user_agent.strip() == "":
		abort(403)
		
	if any(bad in user_agent for bad in known_bad_bots):
		abort(403)
		
@app.route('/favicon.ico')
def favicon():
	return redirect(url_for('static', filename='images/favicon.ico'))
	
# </editor-fold>

if __name__ == '__main__':
	app.run(debug=True, port=5000, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
