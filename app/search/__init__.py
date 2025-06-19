import requests
from flask import Blueprint

from .config import TOSHI_URL, AUTH, INDEX_NAME
from .routes import health

search_bp = Blueprint("search", __name__)


def ensure_index():
	if not health():
		print("Toshi is not running. Skipping index creation.")
		return
	
	# First, get list of indexes
	list_url = f"{TOSHI_URL}/_list"
	try:
		resp = requests.get(list_url, auth=AUTH)
		resp.raise_for_status()
		indexes = resp.json().get("indexes", [])
	except Exception as e:
		print(f"Error checking index list: {e}")
		raise
	
	# If the index already exists, skip creation
	if INDEX_NAME in indexes:
		print(f"Index '{INDEX_NAME}' already exists.")
		return
	
	# Define index schema
	payload = [
		{
			"name": "title",
			"type": "text",
			"options": {
				"indexing": {"record": "position", "tokenizer": "default"},
				"stored": True
			}
		},
		{
			"name": "id",
			"type": "u64",
			"options": {"indexed": True, "stored": True}
		},
		{
			"name": "content",
			"type": "text",
			"options": {
				"indexing": {"record": "position", "tokenizer": "default"},
				"stored": True
			}
		},
		{
			"name": "date_posted",
			"type": "i64",
			"options": {"indexed": True, "stored": True}
		},
		{
			"name": "location_name",
			"type": "text",
			"options": {
				"indexing": {"record": "position", "tokenizer": "default"},
				"stored": True
			}
		}
	]
	
	# Attempt to create the index
	create_url = f"{TOSHI_URL}/{INDEX_NAME}/_create"
	create_resp = requests.put(create_url, json=payload, auth=AUTH)
	
	if create_resp.status_code not in (200, 201):
		print("Failed to create index:")
		try:
			print(create_resp.json())
		except Exception:
			print(create_resp.text)
		raise Exception("Index creation failed")
	
	print(f"Index '{INDEX_NAME}' successfully created.")


ensure_index()

from . import routes  # import routes at the end to avoid circular imports
