import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, login_user, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
import cloudinary.uploader
from app import db
from .extensions import mail
from app.models import Post, User

s = URLSafeTimedSerializer(os.environ.get("SECRET_KEY"))

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
		image = request.files['image']

		if not title or not content:
			flash('Please enter both title and content', 'danger')
		else:
			
			if image:
				upload_result = cloudinary.uploader.upload(image)
				image_url = upload_result["secure_url"]  # Get the Cloudinary URL
				
				# Save post with image URL in database
				new_post = Post(title=title, content=content, image_url=image_url, user_id=current_user.id)
				db.session.add(new_post)
				db.session.commit()
			else:
				# Save post without image URL in database
				post = Post(title=title, content=content, user_id=current_user.id)
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
		try:
			user = User()
			user.username = username
			user.email = email
			user.set_password(password)
			db.session.add(user)
			db.session.commit()
		except:
			db.session.rollback()
			flash('Email already registered. Please log in or chose another email', 'danger')
			return redirect(url_for('main.login'))
		return redirect(url_for('main.login'))
	return render_template('signup.html', title='Sign Up')


@main.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('main.home'))


# noinspection PyUnreachableCode
@main.route('/password', methods=['GET', 'POST'])
def password_reset():
	if request.method == 'POST':
		email = request.form['email']
		if not email:
			flash('Please enter your email', 'danger')
			return  redirect(url_for('main.password_reset'))
		
		user = User.query.filter_by(email=email).first()
		if user:

			# Generate a secure token
			token = s.dumps(email, salt='password-reset-salt')
	
			# Create reset link
			reset_url = url_for('main.password_reset_token', token=token, _external=True)
	
			# Send the email
			msg = Message('Password Reset Request - WayPointsAndWonders',
							  recipients=[email])
			msg.body = render_template('email/password_email.txt', reset_url=reset_url)
			
			msg.html = render_template('email/password_email.html', reset_url=reset_url)
			
			mail.send(msg)
	
			flash('Check your email for password reset instructions.', 'info')
			return redirect(url_for('main.home'))
		else:
			flash('Email not found', 'danger')
			return redirect(url_for('main.password_reset'))

	return render_template('password/password_reset.html', title='Password Reset')


@main.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset_token(token):
	try:
		email = s.loads(token, salt='password-reset-salt', max_age=3600)  # Token expires in 1 hour
	except:
		flash('Invalid or expired token.', 'danger')
		return redirect(url_for('main.password_reset'))

	if request.method == 'POST':
		new_password = request.form['password_1']
		conferm_password = request.form['password_2']

		if not new_password or not conferm_password:
			flash('Please enter both password', 'danger')
			return redirect(url_for('main.password_reset_token', token=token))

		if new_password != conferm_password:
			flash('Passwords do not match', 'danger')
			return redirect(url_for('main.password_reset_token', token=token))
		user = User.query.filter_by(email=email).first()
		if user:
			user.set_password(new_password)
			flash('Your password has been updated.', 'success')
			return redirect(url_for('main.login'))
	return render_template('password/password_reset_phase2.html', title='Reset Password', token=token)

@main.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.user_id != current_user.id:
		abort(403)
	if request.method == 'POST':
		post.title = request.form['title']
		post.content = request.form['content']
		db.session.commit()
		return redirect(url_for('main.post', post_id=post.id))
	return render_template('edit_post.html', title='Edit Post', post=post)


@main.route('/delete/<int:post_id>', methods=['POST', 'GET'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.user_id != current_user.id:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!', 'success')
	return redirect(url_for('main.home'))


# noinspection PyUnreachableCode
@main.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
	return render_template('error.html', title='Profile', functionality='Profile',
	                       message='This feature has not been implemented yet, please contact an admin if you need this feature')
	if current_user.is_anonymous or current_user.id != user_id:
		return render_template('error.html', title='Profile', functionality='Profile', message='You do not have access to this page')
	user = User.query.get_or_404(user_id)
	# TODO: Add profile page (profile.html, takes user= User())
	return render_template('profile.html', title='Profile', user=user)