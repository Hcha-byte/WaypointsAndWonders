from flask_login import current_user, login_required
from functools import wraps
from flask import flash, redirect, url_for


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Access denied: Admins only", "danger")
            return redirect(url_for("main.home"))  # Redirect non-admin users
        return f(*args, **kwargs)
    return decorated_function
