import os

import requests
from flask import request, Response, render_template, flash, redirect, url_for

from . import search_bp
from ..decoraters import admin_required
from ..models import Post

MEILI_URL = os.getenv("MEILI_URL", "http://meilisearch:7700")
MEILI_API_KEY = os.getenv("MEILI_API_KEY")


@search_bp.route('/', methods=['GET', 'POST'])
def search():
	return render_template('search.html', title='Search')


@search_bp.route("meili/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@admin_required
def proxy_meilisearch(path):
	# Forward the request to MeiliSearch
	url = f"{MEILI_URL}/{path}"
	headers = {key: value for key, value in request.headers if key != 'Host'}
	headers["X-Meili-API-Key"] = MEILI_API_KEY
	
	response = requests.request(
		method=request.method,
		url=url,
		headers=headers,
		data=request.get_data(),
		cookies=request.cookies,
		allow_redirects=False
	)
	
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
