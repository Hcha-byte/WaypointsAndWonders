from flask import render_template
from app.models import Post
from . import posts_bp


@posts_bp.route('/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)
