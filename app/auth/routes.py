import requests
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message

from app.database import db
from app.extensions import mail, google
from app.models import User
from . import auth_bp
from ..extensions import serializer


@auth_bp.route('/login', methods=['GET', 'POST'])
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
			return redirect(url_for('auth.login'))
		
		user = User.query.filter_by(username=username).first()
		if user and user.check_password(password):
			login_user(user, remember=remember_me)
			next_url = request.args.get('next')
			return redirect(next_url or url_for('main.home'))
		else:
			flash('Invalid username or password', 'danger')
	return render_template('login.html', title='Login')


@auth_bp.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('main.home'))


@auth_bp.route('/login/google')
def login_google():
	redirect_uri = url_for('auth.authorize_google', _external=True)
	return google.authorize_redirect(redirect_uri)


@auth_bp.route('/authorize/google')
def authorize_google():
	token = google.authorize_access_token()
	user_info = google.get('userinfo').json()
	user = User.query.filter_by(id=user_info['id']).first()
	
	if not user:
		user = User()
		user.id = user_info['id']
		user.username = user_info['given_name']
		user.email = user_info['email']
		user.image_url = user_info.get('picture')
		user.is_oauth = True
		db.session.add(user)
		db.session.commit()
	
	login_user(user, remember=True)
	return redirect(url_for('auth.profile', user_id=user.id))


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		flash('You are already logged in', 'info')
		return redirect(url_for('main.home'))
	
	if request.method == 'POST':
		
		# ✅ reCAPTCHA validation
		recaptcha_response = request.form.get('g-recaptcha-response')
		if not recaptcha_response:
			flash('Please complete the reCAPTCHA challenge.', 'danger')
			return redirect(url_for('auth.signup'))
		# Verify reCAPTCHA with Google
		verify_url = 'https://www.google.com/recaptcha/api/siteverify'
		data = {
			'secret':   current_app.config['RECAPTCHA_SECRET_KEY'],
			'response': recaptcha_response,
			'remoteip': request.remote_addr
		}
		r = requests.post(verify_url, data=data)
		result = r.json()
		if not result.get('success'):
			flash('reCAPTCHA verification failed. Please try again.', 'danger')
			return redirect(url_for('auth.signup'))
		
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
		except Exception:
			db.session.rollback()
			flash('Email already registered. Please log in or chose another email', 'danger')
			return redirect(url_for('auth.login'))
		try:
			current_user.login_user(user)
		except Exception:
			pass
		flash('Your account has been created!', 'success')
		return redirect(url_for('main.home'))
	return render_template('signup.html', title='Sign Up')


@auth_bp.route('/password', methods=['GET', 'POST'])
def password_reset():
	if request.method == 'POST':
		email = request.form['email']
		if not email:
			flash('Please enter your email', 'danger')
			return redirect(url_for('auth.password_reset'))
		
		user = User.query.filter_by(email=email).first()
		if user:
			
			# Generate a secure token
			token = serializer.dumps(email, salt='password-reset-salt')
			
			# Create a reset link
			reset_url = url_for('auth.password_reset_token', token=token, _external=True)
			
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
			return redirect(url_for('auth.password_reset'))
	
	return render_template('password/password_reset.html', title='Password Reset')


@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset_token(token):
	try:
		email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # Token expires in 1 hour
	except:
		flash('Invalid or expired token.', 'danger')
		return redirect(url_for('auth.password_reset'))
	
	if request.method == 'POST':
		new_password = request.form['password_1']
		conferm_password = request.form['password_2']
		
		if not new_password or not conferm_password:
			flash('Please enter both password', 'danger')
			return redirect(url_for('auth.password_reset_token', token=token))
		
		if new_password != conferm_password:
			flash('Passwords do not match', 'danger')
			return redirect(url_for('auth.password_reset_token', token=token))
		user = User.query.filter_by(email=email).first()
		if user:
			user.set_password(new_password)
			flash('Your password has been updated.', 'success')
			return redirect(url_for('auth.login'))
	return render_template('password/password_reset_phase2.html', title='Reset Password', token=token)


@auth_bp.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
	if current_user.id != str(user_id) or not current_user.is_admin:
		return render_template('error.html', title='Profile', functionality='Profile',
		                       message='You do not have access to this page')
	user = User.query.get_or_404(str(user_id))
	return render_template('profile.html', title='Profile', user=user)
