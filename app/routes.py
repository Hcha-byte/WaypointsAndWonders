from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user

from app import db
from app.models import Post, User

main = Blueprint('main', __name__)


@main.route('/index')
@main.route('/')
@login_required
def home():

	posts = Post.query.all()

	return render_template('index.html', title='Home', posts=posts)

@main.route('/post/<int:post_id>')
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post=post)

@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_post():
	if request.method == 'POST':

		title = request.form['title']
		content = request.form['content']

		if not title or not content:
			flash('Please enter both title and content', 'danger')
		else:
			post = Post(title=title, content=content)
			db.session.add(post)
			db.session.commit()
			flash('Your post has been published!', 'success')
			return redirect(url_for('main.home'))
	
	return render_template('add_post.html', title='Add Post')


@main.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		flash('You are already logged in', 'info')
		return redirect(url_for('main.home'))
	
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		remember_me = request.form.get('remember_me', False)
		
		if not username or not password:
			flash('Please enter both username and password', 'danger')
			return redirect(url_for('main.login'))

		user = User.query.filter_by(username=username).first()
		if user and user.check_password(password):
			login_user(user, remember=remember_me)
			next_url = request.args.get('next')
			if next_url:
				return redirect(next_url)
			else:
				return redirect(url_for('main.home'))
	return render_template('login.html', title= 'Login')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		username = request.form['username']
		email = request.form['email']
		password = request.form['password']
		confirm_password = request.form['confirm_password']

		if not username or not email or not password or not confirm_password:
			flash('Please enter all fields', 'danger')
			return redirect(url_for('main.signup'))

		if password != confirm_password:
			flash('Passwords do not match', 'danger')
			return redirect(url_for('main.signup'))
		
		user = User()
		user.username = username
		user.email = email
		user.set_password(password)
		db.session.add(user)
		db.session.commit()
		return redirect(url_for('main.login'))
	return render_template('signup.html', title='Sign Up')


@main.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('main.home'))