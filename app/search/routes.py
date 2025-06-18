import os

import requests
from flask import request, render_template, session, jsonify
from rq.job import Job

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


@search_bp.route('/index_all', methods=['GET', 'POST'])
@admin_required
def index_all():
	"""Index all documents in the MeiliSearch index."""
	pass


@search_bp.route('/reindex_all_progress')
@admin_required
def reindex_all_progress():
	job_id = session.get('reindex_job_id')
	if not job_id:
		return jsonify({"status": "not_started"})
	
	try:
		job = Job.fetch(job_id, connection=redis_conn)
		
		progress = int(redis_conn.get("reindex_progress") or 0)
		total = int(redis_conn.get("reindex_total") or 1)
		percent = int((progress / total) * 100)
		
		if job.is_finished:
			return jsonify({"status": "finished", "progress": 100})
		elif job.is_failed:
			return jsonify({"status": "failed", "error": str(job.latest_result())})
		else:
			return jsonify({"status": "in_progress", "progress": percent})
	except Exception as e:
		return jsonify({"status": "error", "message": str(e)})
