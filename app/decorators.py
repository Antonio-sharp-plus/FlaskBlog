from functools import wraps

from flask import abort
from flask_login import current_user
from app.models import BlogPost


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if current_user.email != "antonicoa2014@gmail.com":
            abort(403)
        return function(*args, **kwargs)

    return wrapper


def edit_and_delete_permission(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        post_id = kwargs.get('post_id')
        post = BlogPost.query.get_or_404(post_id)

        if not current_user.is_authenticated:
            abort(403)

        if current_user.email != "antonicoa2014@gmail.com" or current_user.id != post.author_id:
            abort(403)

        return function(*args, **kwargs)

    return wrapper
