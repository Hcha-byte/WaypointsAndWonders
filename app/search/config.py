import os

TOSHI_URL = "https://typesense-main.up.railway.app"
AUTH = os.environ.get("TYPESENSE_API_KEY", '')
COLLECTION_NAME = "posts"
