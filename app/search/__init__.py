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


from . import routes  # import routes at the end to avoid circular imports
