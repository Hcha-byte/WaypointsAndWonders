import datetime

from flask import render_template, Response, render_template_string, url_for, redirect, request
from flask_login import current_user
from sqlalchemy import desc

from app.models import Post
from . import main_bp  # import the blueprint
from ..decoraters import login_bot, is_bot


@main_bp.route('/')
def welcome():
	args = request.args.get('testing')
	
	if args == 't':
		print('Testing logged on welcome')
		return render_template('welcome.html', title='Welcome')
	
	if not is_bot():
		if current_user.is_authenticated:
			return redirect(url_for('main.home'))
		else:
			return render_template('welcome.html', title='Welcome')
	else:
		return render_template_string("<h1>Welcome to WayPointsAndWonders!</h1>")


@main_bp.route('/index')
@login_bot
def home():
	if not is_bot():
		
		posts = Post.query.order_by(desc(Post.date_posted)).all()
		
		return render_template('index.html', title='Home', posts=posts)
	else:
		return render_template('index.html', title='Home', posts=None)


@main_bp.route('/sitemap.xml')
def sitemap():
	"""Generate an XML sitemap dynamically from the database."""
	base_url = "https://waypointsandwonders.com"
	lastmod = datetime.datetime.now().strftime("%Y-%m-%d")
	urls = [
		{"loc": f"{base_url}{url_for('main.welcome')}", "lastmod": lastmod, "priority": "0.7"},
		{"loc": f"{base_url}{url_for('main.home')}", "lastmod": lastmod, "priority": "1.0"},
	]
	
	# Fetch all published blog posts
	posts = Post.query.all()
	for post in posts:
		urls.append({
			"loc": f"{base_url}/post/{post.id}",
			"lastmod": post.date_posted.strftime("%Y-%m-%d"),
			"priority": "0.5"
		})
	
	sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {''.join(
		f'<url><loc>{url["loc"]}</loc><lastmod>{url["lastmod"]}</lastmod><changefreq>weekly</changefreq><priority>{url["priority"]}</priority></url>'
		for url in urls
	)}
    </urlset>
    """
	
	return Response(sitemap_xml, mimetype="application/xml")


@main_bp.route('/robots.txt')
def robots():
	content = f"""User-agent: *
 
Disallow: {url_for('admin.admin')}
Disallow: {url_for('auth.login')}
Disallow: {url_for('auth.signup')}
Disallow: {url_for('auth.logout')}
Disallow: {url_for('auth.password_reset')}
Disallow: {url_for('auth.password_reset_token', token='')}
Disallow: {url_for('auth.authorize_google')}

Allow: {url_for('main.welcome')}
Allow: {url_for('main.home')}


Sitemap: https://waypointsandwonders.com/sitemap.xml
"""
	return Response(content, mimetype='text/plain')


@main_bp.route('/terms_and_privacy')
def terms_and_privacy():
	return render_template('terms_and_privacy/terms_and_privacy.html')


@main_bp.route('/favicon.ico')
def favicon():
	return redirect(url_for('static', code=301, filename='images/favicon.ico'))
