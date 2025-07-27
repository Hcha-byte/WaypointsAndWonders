import json

from flask import Blueprint
from typesense.exceptions import ObjectNotFound

from .config import COLLECTION_NAME
from ..extensions import get_typesense_client

search_bp = Blueprint("search", __name__)


def ensure_index():
	# Check if collection exists
	client = get_typesense_client()
	try:
		client.collections[COLLECTION_NAME].retrieve()
	except ObjectNotFound:
		# Only create if not exists
		schema = {
			"name":                  COLLECTION_NAME,
			"fields":                [
				{
					"name": "title",
					"type": "string"
				},
				{
					"name": "id",
					"type": "string"
				},
				{
					"name": "content",
					"type": "string"
				},
				{
					"name": "date_posted",
					"type": "int64"
				},
				{
					"name": "location_name",
					"type": "string"
				}
			],
			"default_sorting_field": "date_posted"
		}
		
		client.collections.create(schema)


def to_ndjson(docs):
	return '\n'.join(json.dumps(doc) for doc in docs)


import time
import typesense


def ensure_index_with_retry(client=None, collection_name=COLLECTION_NAME, max_attempts=5, delay=3):
	if client is None:
		from app.extensions import get_typesense_client
		client = get_typesense_client()
	for attempt in range(max_attempts):
		try:
			client.collections[collection_name].retrieve()
			print("✅ Typesense index is ready.")
			return ensure_index()
		except typesense.exceptions.ObjectNotFound:
			print(f"⚠️  Collection '{collection_name}' not found.")
			return None  # or create it here if needed
		except typesense.exceptions.TypesenseClientError as e:
			print(f"❌ Error talking to Typesense (attempt {attempt + 1}): {e}")
			time.sleep(delay)
		except Exception as e:
			print(f"🔥 Unexpected error (attempt {attempt + 1}): {e}")
			time.sleep(delay)
	
	print("❌ Failed to connect to Typesense after multiple attempts.")
	return None


from . import routes  # import routes at the end to avoid circular imports
