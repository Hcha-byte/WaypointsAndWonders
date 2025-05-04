import datetime
from flask import render_template, Response, render_template_string
from app.models import Post
from ..decoraters import login_bot, is_bot

from . import main_bp  # import the blueprint

@main_bp.route('/')
def welcome():
    if not is_bot():
        return render_template('welcome.html', title='Welcome')
    else:
        return render_template_string("<h1>Welcome to WayPointsAndWonders!</h1>")

@main_bp.route('/index')
@login_bot
def home():
    if not is_bot():
        posts = Post.query.all()
        return render_template('index.html', title='Home', posts=posts)
    else:
        return render_template('index.html', title='Home', posts=None)

@main_bp.route('/sitemap.xml')
def sitemap():
    """Generate an XML sitemap dynamically from the database."""
    base_url = "https://waypointsandwonders.com"
    lastmod = datetime.datetime.now().strftime("%Y-%m-%d")
    urls = [
        {"loc": f"{base_url}/", "lastmod": lastmod, "priority": "0.3"},
        {"loc": f"{base_url}/index", "lastmod": lastmod, "priority": "1.0"},
        # TODO: Add other pages to the sitemap
    ]

    # Fetch all published blog posts
    posts = Post.query.all()
    for post in posts:
        urls.append({
            "loc": f"{base_url}/post/{post.id}",
            "lastmod": post.date_posted.strftime("%Y-%m-%d"),
            "priority": "0.1"
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
