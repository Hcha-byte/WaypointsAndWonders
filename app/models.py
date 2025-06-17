import re
from typing import overload, List, Union

from flask_login import UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from .database import db
from .decoraters import background_job
from .extensions import client, redis_conn


def generate_next_post_id():
	last_post = Post.query.order_by(db.cast(Post.id, db.Integer).desc()).first()
	
	if last_post and last_post.id.isdigit():
		return str(int(last_post.id) + 1)
	return "1"


def reindex_all():
	print("Starting reindex")
	
	index = client.index('posts')
	posts = Post.query.all()
	batch_size = 100
	total = len(posts)
	
	for i in range(0, total, batch_size):
		batch = posts[i:i + batch_size]
		docs = [{
			'id': post.id,
			'title': post.title,
			'content': post.content
		} for post in batch]
		
		try:
			index.add_documents(docs)
			# Update progress
			print(f"Indexed batch {i // batch_size + 1}")
		except Exception as e:
			print(f"Error indexing batch {i // batch_size + 1}: {e}")
			raise e  # This will cause job to be marked as failed
	print("Reindex complete")


# Ensure we hit 100%


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	title = db.Column(db.String(200), nullable=False)
	content = db.Column(db.Text, nullable=False)
	date_posted = db.Column(db.DateTime, default=db.func.now())
	user_id = db.Column(db.String(255), db.ForeignKey('user.id'), nullable=True,
	                    default=lambda: current_user.id if current_user.is_authenticated and current_user.is_admin else None)
	image_url = db.Column(db.ARRAY(db.String), nullable=True)
	
	location_name = db.Column(db.String(200), nullable=True)
	lat = db.Column(db.Float, nullable=True)
	long = db.Column(db.Float, nullable=True)
	
	@staticmethod
	def search_posts(query):
		index = client.index('posts')
		results = index.search(query)
		ids = [hit['id'] for hit in results['hits']]
		return Post.query.filter(Post.id.in_(ids)).all()
	
	@staticmethod
	def index_post(post):
		index = client.index('posts')
		index.add_documents([{
			'id': post.id,
			'title': post.title,
			'content': post.content,
			'created_at': post.timestamp.isoformat()  # Optional
		}])
	
	@background_job
	@staticmethod
	def reindex_all():
		index = client.index('posts')
		posts = Post.query.all()
		batch_size = 100
		total = len(posts)
		redis_conn.set("reindex_total", total)
		
		for i in range(0, total, batch_size):
			batch = posts[i:i + batch_size]
			docs = [{
				'id': post.id,
				'title': post.title,
				'content': post.content
			} for post in batch]
			
			try:
				index.add_documents(docs)
				redis_conn.set("reindex_progress", i + len(batch))  # Update progress
			except Exception as e:
				print(f"Error indexing batch {i // batch_size + 1}: {e}")
				raise e  # This will cause job to be marked as failed
		
		redis_conn.set("reindex_progress", total)  # Ensure we hit 100%
	
	# noinspection PyNestedDecorators
	@overload
	@staticmethod
	def get_urls(char_list: List[str]) -> List[str]:
		...
	
	@overload
	def get_urls(self) -> List[str]:
		...
	
	# noinspection PyMethodParameters
	def get_urls(self_or_char_list: Union['Post', List[str]]) -> List[str]:
		# Detect whether this is called with a char list or from an instance
		if isinstance(self_or_char_list, list):
			char_list = self_or_char_list
		else:
			# called as an instance method
			self = self_or_char_list
			char_list = self.image_url
		
		if not char_list:
			return []
		
		# Step 1: Remove all junk commas
		chars_only = [c for c in char_list if c != ',']
		
		# Step 2: Rebuild the string
		full_str = ''.join(chars_only)
		
		# Step 3: Strip outer {}
		if full_str.startswith('{') and full_str.endswith('}'):
			full_str = full_str[1:-1]
		
		# Step 4: Insert comma before every http/https after the first one
		# noinspection RegExpRedundantEscape
		full_str = re.sub(r'(https?:\/\/)', r',\1', full_str, count=0)
		
		# Step 5: Split on commas
		urls = [url.strip() for url in full_str.split(',') if url.strip()]
		
		return urls


def generate_next_user_id():
	last_user = User.query.filter_by(is_oauth=False).order_by(db.cast(User.id, db.Integer).desc()).first()
	
	if last_user and last_user.id.isdigit():
		return str(int(last_user.id) + 1)
	return "1"


class User(db.Model, UserMixin):
	id = db.Column(db.String(255), primary_key=True, default=generate_next_user_id)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_url = db.Column(db.String, nullable=False,
	                      default='https://res.cloudinary.com/dao2ekwrd/image/upload/v1741910294/WPAW/z9hnukyaz0f0i7osnamz.jpg')
	is_admin = db.Column(db.Boolean, nullable=False, default=False)
	is_oauth = db.Column(db.Boolean, default=False, nullable=False)
	password_hash = db.Column(db.String, nullable=True)
	
	def make_admin(self):
		self.is_admin = True
		db.session.commit()
	
	def change_image(self, image_file):
		self.image_url = image_file
		db.session.commit()
	
	def change_username(self, username):
		self.username = username
		db.session.commit()
	
	def change_email(self, email):
		self.email = email
		db.session.commit()
	
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
		db.session.commit()
	
	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	@staticmethod
	def user_loder(user_id):
		return User.query.get(user_id)
