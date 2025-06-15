import os

import brotli
import requests
from flask import request, Response, render_template, flash, redirect, url_for

from . import search_bp
from ..decoraters import admin_required
from ..models import Post

MEILI_URL = os.getenv("MEILI_URL", "http://meilisearch.railway.internal:7700")
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


@search_bp.route("/meili/", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@admin_required
def proxy_meilisearch_root():
	url = f"{MEILI_URL.rstrip('/')}/"
	
	data = request.get_data() if request.method in ['POST', 'PUT', 'PATCH'] else None
	
	headers = {
		k: v for k, v in request.headers
		if k.lower() not in ['host', 'content-length', 'content-encoding', 'transfer-encoding', 'authorization']
	}
	headers["Authorization"] = f"Bearer {MEILI_API_KEY}"
	if data:
		headers["Content-Type"] = request.headers.get("Content-Type", "application/json")
	
	response = requests.request(
		method=request.method,
		url=url,
		headers=headers,
		data=data,
		cookies=request.cookies,
		allow_redirects=True
	)
	
	content = response.content
	content_encoding = response.headers.get("Content-Encoding", "").lower()
	
	# Only decode if it's Brotli
	if content_encoding == "br":
		try:
			content = brotli.decompress(content)
		except brotli.error as e:
			return Response(
				f"Brotli decompression failed: {str(e)}", status=500
			)
	
	return Response(
		content,
		status=response.status_code,
		headers={k: v for k, v in response.headers.items() if k.lower() not in [
			'content-encoding', 'transfer-encoding', 'content-length'
		]},
		content_type=response.headers.get("Content-Type", "application/json")
	)


@search_bp.route("/meili/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@admin_required
def proxy_meilisearch(path):
	path = path.lstrip('/')
	url = f"{MEILI_URL.rstrip('/')}/{path}"
	
	data = request.get_data() if request.method in ['POST', 'PUT', 'PATCH'] else None
	
	headers = {
		k: v for k, v in request.headers
		if k.lower() not in ['host', 'content-length', 'content-encoding', 'transfer-encoding', 'authorization']
	}
	headers["Authorization"] = f"Bearer {MEILI_API_KEY}"
	if data:
		headers["Content-Type"] = request.headers.get("Content-Type", "application/json")
	
	response = requests.request(
		method=request.method,
		url=url,
		headers=headers,
		data=data,
		cookies=request.cookies,
		allow_redirects=True
	)
	
	content = response.content
	if response.headers.get("Content-Encoding") == "br":
		import brotli
		content = brotli.decompress(content)
	
	return Response(
		content,
		status=response.status_code,
		headers={k: v for k, v in response.headers.items() if k.lower() not in [
			'content-encoding', 'transfer-encoding', 'content-length'
		]},
		content_type=response.headers.get("Content-Type", "application/json")
	)


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


@search_bp.route('/index_all')
@admin_required
def index_all():
	"""Index all documents in the MeiliSearch index."""
	if request.args.get('auth') != MEILI_API_KEY:
		return render_template('search_auth.html', title='Confirm Reindex')
	else:
		Post.reindex_all()
		flash('Reindex started', 'success')
		return redirect(url_for('main.home'))
