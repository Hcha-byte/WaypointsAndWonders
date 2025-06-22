from app.extensions import client
from app.models import Post
from app.search import to_ndjson


def search_posts(query, location_filter=None, sort_by_date_desc=True, per_page=20):
	search_parameters = {
		"q": query,
		"query_by": "title,content,location_name",
		"sort_by": "date_posted:desc" if sort_by_date_desc else "date_posted:asc",
		"per_page": per_page
	}
	if location_filter:
		search_parameters["filter_by"] = f"location_name:={location_filter}"
	
	try:
		results = client.collections["posts"].documents.search(search_parameters)
		ids = [int(hit["document"]["id"]) for hit in results.get("hits", [])]
		
		posts = Post.query.filter(Post.id.in_(ids)).all()
		
		# Optional: sort posts in Typesense order
		posts_by_id = {post.id: post for post in posts}
		posts = [posts_by_id[pid] for pid in ids if pid in posts_by_id]
		
		return posts
	except Exception as e:
		print("Search failed:", e)
		return []


def index_post(post):
	document = {
		"id": int(post.id),
		"title": post.title,
		"content": post.content,
		"date_posted": int(post.date_posted.timestamp()),  # or post.date_posted if already int
		"location_name": post.location_name
	}
	
	try:
		client.collections['posts'].documents.upsert(document)
		print(f"Indexed post {post.id}")
	except Exception as e:
		print(f"Failed to index post {post.id}: {e}")


def bulk_index_posts():
	posts = Post.query.all()
	
	documents = []
	for post in posts:
		documents.append({
			"id": str(post.id),
			"title": post.title,
			"content": post.content,
			"date_posted": int(post.date_posted.timestamp()),
			"location_name": post.location_name
		})
	response = None
	try:
		json_docs = to_ndjson(documents)
		response = client.collections['posts'].documents.import_(
			json_docs, {'action': 'upsert'}
		)
		print("Bulk indexing completed.")  # Optional: review any import errors
	except Exception as e:
		print(f"Failed to bulk index: {e}")
	
	return response
