import io
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import json
from datetime import datetime, timezone
import cloudinary.uploader
from app.models import Post
from app.database import db

LOG_FILE = "trip_import_log.txt"
BASE_PATH = "polarsteps_backup/trip/washington_12929411/"
CURRENT_DIRECTORY = "washington_12929411"


def log(message, to_file=True):
	print(message)
	if to_file:
		with open(LOG_FILE, "a") as f:
			f.write(message + "\n")


def get_img(step_id: str, step_name: str) -> list:
	start_path: str = os.path.join("/Users/harvey/Code/python/WaypointsAndWonders", BASE_PATH, f"{step_name}_{step_id}", "photos")
	
	if not os.path.exists(start_path):
		log(f"⚠️  No photos folder for step '{step_name}' ({step_id})")
		return []
	
	img_paths = os.listdir(start_path)
	imgs = []
	for img_path in img_paths:
		if not os.path.exists(os.path.join(start_path, img_path)):
			log(f"❌ Image '{img_path}' does not exist")
			return []
		if img_path.endswith(".jpg"):
			try:
				with open(os.path.join(start_path, img_path), "rb") as f :
					img = io.BytesIO(f.read())
			except Exception as e:
				log(f"❌ Failed to open image '{img_path}': {e}")
				return []
			try:
				img = cloudinary.uploader.upload(img, use_asset_folder_as_public_id_prefix=True, asset_folder=f"WPAW/posts/{CURRENT_DIRECTORY}")
			except Exception as e:
				log(f"❌ Failed to upload image '{img_path}': {e}")
				return []
			img = img.get("secure_url")
			imgs += [img]
			log(f"✅ Imported img '{img_path}' to cloudinary, '{img}'")
	return imgs


def import_steps_as_posts(trip_data):
	steps = trip_data.get("all_steps", [])
	if not steps:
		log(f"⚠️  Skipped trip '{trip_data.get('name', 'Unknown')}' (no steps)")
		return
	
	user_id = 1
	imported = 0
	for step in steps:
		try:
			imgs = get_img(str(step.get("id")), step.get("slug"))
			post = Post(
				title=step.get("name", "Untitled Step"),
				content=step.get("description", "ERROR: No description"),
				date_posted=datetime.fromtimestamp(step.get("start_time", 0), tz=timezone.utc),
				user_id=user_id,
				image_url=imgs if imgs else trip_data.get("cover_photo_path", None),
				location_name=step.get("location", {}).get("name", None),
				lat=step.get("location", {}).get("lat", None),
				long=step.get("location", {}).get("lon", None),
			)
			db.session.add(post)
			imported += 1
			db.session.commit()
			log(f"✅ Added step '{step.get('name')}' in trip '{trip_data.get('name')}'")
		except Exception as e:
			db.session.rollback()
			log(f"❌ Failed to add step '{step.get('name')}' in trip '{trip_data.get('name')}': {e}")
	
	
	log(f"✅ Imported {imported} steps from trip '{trip_data.get('name', 'Unnamed')}'")


def import_all_trips_from_directory(base_dir):
	log(f"\n🗂️ Starting import from: {base_dir}")
	for root, dirs, files in os.walk(base_dir):
		for file in files:
			if file == "trip.json":
				path = os.path.join(root, file)
				try:
					with open(path, "r") as f:
						trip_data = json.load(f)
						import_steps_as_posts(trip_data)
				except Exception as e:
					db.session.rollback()
					log(f"❌ Failed to process {path}: {e}")
	log("✅ Import process complete.\n")
	log("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&\n")


# Example usage:
if __name__ == "__main__":
	from run import app

	
	base_directory = os.path.join("/Users/harvey/Code/python/WaypointsAndWonders", BASE_PATH)
	with app.app_context():
		import_all_trips_from_directory(base_directory)
