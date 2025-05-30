import cloudinary.uploader
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..decoraters import admin_required
from app.models import Post
from app.database import db

from . import admin_bp


@admin_bp.route('/')
@admin_required
def admin():
	posts = Post.query.all()
	return render_template('admin/admin.html', title='Admin', posts=posts)


@admin_bp.route('/add', methods=['GET', 'POST'])
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
				image_url = upload_result["secure_url"]
				new_post = Post(title=title, content=content, image_url=image_url, user_id=current_user.id)
				db.session.add(new_post)
				db.session.commit()
				flash('Your post has been published with an image!', 'success')
			else:
				post = Post(title=title, content=content, user_id=current_user.id)
				db.session.add(post)
				db.session.commit()
				flash('Your post has been published!', 'success')
			
			return redirect(url_for('main.home'))
	
	return render_template('admin/add_post.html', title='Add Post')


@admin_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def edit_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.user_id != current_user.id:
		abort(403)
	if request.method == 'POST':
		post.title = request.form['title']
		post.content = request.form['content']
		db.session.commit()
		return redirect(url_for('posts.view_post', post_id=post.id))
	return render_template('admin/edit_post.html', title='Edit Post', post=post)


@admin_bp.route('/delete/<int:post_id>', methods=['POST', 'GET'])
@admin_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.user_id != current_user.id:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!', 'success')
	return redirect(url_for('main.home'))
