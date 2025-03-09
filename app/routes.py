from flask import Blueprint, render_template
from app.models import Post

main = Blueprint('main', __name__)

@main.route('/index')
@main.route('/')
def home():

    posts = Post.query.all()

    return render_template('index.html', title='Home', posts=posts)

@main.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

