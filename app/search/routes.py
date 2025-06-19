import requests
from flask import request, render_template

from . import search_bp, TOSHI_URL, AUTH
from ..decoraters import admin_required
from ..models import Post


@search_bp.route('/', methods=['GET', 'POST'])
def search():
	q = request.form.get('q', '')
	sectoin = request.form.get('section', '')
	if q:
		qe = \
			{
				"query": {
					"term": {
						sectoin: q
					}
				},
				"limit": 20
			}
		
		posts = Post.search_posts(qe)
		return render_template('search.html', posts=posts, query=q, title='Search')
	
	return render_template('search.html', title='Search')


@search_bp.route('/index_all', methods=['GET', 'POST'])
@admin_required
def index_all():
	"""Index all documents in the MeiliSearch index."""
	pass


@search_bp.route('/health')
def health():
	r = requests.get(f"{TOSHI_URL}/", auth=AUTH)
	
	if r.status_code == 200 or r.status_code == 201:
		return True
	
	return False
