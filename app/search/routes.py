import os

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


@search_bp.route("meili/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@admin_required
def proxy_meilisearch(path):
	# Forward the request to MeiliSearch
	# Remove any leading slashes from the path to prevent double slashes
	path = path.lstrip('/')
	url = f"{MEILI_URL.rstrip('/')}/{path}"
	headers = {key: value for key, value in request.headers if key != 'Host'}
	headers["X-Meili-MASTER-Key"] = MEILI_API_KEY
	
	while True:
		response = requests.request(
			method=request.method,
			url=url,
			headers=headers,
			data=request.get_data(),
			cookies=request.cookies,
			allow_redirects=True
		)
		# Retry on 5xx errors and 4xx errors
		if not response.status_code == 404:
			break
		else:
			url = f"{MEILI_URL.rstrip('/')}/indexes"
	
	# Forward response back to client
	return Response(
		response.content,
		status=response.status_code,
		headers=dict(response.headers)
	)


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
