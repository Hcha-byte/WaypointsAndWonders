import os

import requests
from flask import request, render_template

from . import search_bp
from .. import TOSHI_URL
from ..decoraters import admin_required
from ..models import Post

MEILI_URL = os.getenv("MEILI_URL", "meilisearch-main.up.railway.app")
# Ensure the URL has a scheme
if not MEILI_URL.startswith(('http://', 'https://')):
	MEILI_URL = f"http://{MEILI_URL}"
MEILI_API_KEY = os.getenv("MEILI_API_KEY")


@search_bp.route('/', methods=['GET', 'POST'])
def search():
	q = request.form.get('q', '')
	if q:
		posts = Post.search_posts(q)
		return render_template('search.html', posts=posts, query=q, title='Search')
	
	return render_template('search.html', title='Search')


@search_bp.route("/test-meili")
@admin_required
def test_meili():
	try:
		response = requests.get(
			f"{MEILI_URL.rstrip('/')}/health",
			headers={"X-Meili-API-Key": MEILI_API_KEY},
			timeout=5
		)
		return response.text, response.status_code
	except Exception as e:
		return f"Failed to connect: {e}", 500


@search_bp.route('/test')
def test():
	try:
		headers = {"Content-Type": "application/json"}
		response_1 = requests.get(
			TOSHI_URL,
			headers=headers,
			timeout=5
		)
		response_2 = requests.get(
			"http://toshi-deploy.railway.internal:8080",
			headers=headers,
			timeout=5
		)
	except Exception as e:
		return f"Failed to connect: {e}", 500
	return f"Response 1: {response_1.text}\nResponse 2: {response_2.text}", 200


@search_bp.route('/curl-toshi')
def curl_toshi():
	import socket
	
	try:
		sock = socket.create_connection(("toshi-deploy.railway.internal", 0), timeout=5)
		sock.sendall(b"GET / HTTP/1.1\r\nHost: toshi-deploy.railway.internal\r\n\r\n")
		response = sock.recv(4096).decode()
		sock.close()
		return f"<pre>{response}</pre>"
	except Exception as e:
		return f"Socket connection failed: {e}", 500


@search_bp.route('/index_all', methods=['GET', 'POST'])
@admin_required
def index_all():
	"""Index all documents in the MeiliSearch index."""
	pass
