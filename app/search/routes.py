from flask import render_template, request

from . import search_bp
from .funtions import search_posts


@search_bp.route('/', methods=['GET', 'POST'])
def search():
	q = request.args.get("q", None)
	if not q:
		return render_template('search.html', title='Search')
	else:
		posts = search_posts(q)
	
	return render_template('search.html', title='Search', posts=posts, q=q)
