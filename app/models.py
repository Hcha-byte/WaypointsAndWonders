from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

from .database import db


def generate_next_post_id():
    last_post = Post.query.order_by(db.cast(Post.id, db.Integer).desc()).first()

    if last_post and last_post.id.isdigit():
        return str(int(last_post.id) + 1)
    return "1"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=generate_next_post_id)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=db.func.now())
    user_id = db.Column(db.String(255), db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String, nullable=True)
    
def generate_next_user_id():
    last_user = User.query.filter_by(is_oauth=False).order_by(db.cast(User.id, db.Integer).desc()).first()

    if last_user and last_user.id.isdigit():
        return str(int(last_user.id) + 1)
    return "1"

class User(db.Model, UserMixin):
    id = db.Column(db.String(255), primary_key=True, default=generate_next_user_id)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_url = db.Column(db.String, nullable=False, default='https://res.cloudinary.com/dao2ekwrd/image/upload/v1741910294/WPAW/z9hnukyaz0f0i7osnamz.jpg')
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
