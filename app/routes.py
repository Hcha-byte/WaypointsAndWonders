from flask import Blueprint, render_template, request, flash, redirect, url_for

from app import db
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

@main.route('/add', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been published!', 'success')
        return redirect(url_for('main.home'))
	
    return render_template('add_post.html', title='Add Post')