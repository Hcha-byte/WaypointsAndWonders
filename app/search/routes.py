import os

import requests
from flask import request, render_template, flash, redirect, url_for

from . import search_bp
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


@search_bp.route('/index_all')
@admin_required
def index_all():
	"""Index all documents in the MeiliSearch index."""
	if request.args.get('auth') != MEILI_API_KEY:
		return render_template('search_auth.html', title='Confirm Reindex', auth=MEILI_API_KEY)
	else:
		Post.reindex_all()
		flash('Reindex started', 'success')
		return redirect(url_for('main.home'))
