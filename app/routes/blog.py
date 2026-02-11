from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from datetime import date

from app.extensions import db
from app.models import BlogPost, Comments
from app.decorators import admin_required, edit_and_delete_permission
from forms import CreatePostForm, CommentForm

bp = Blueprint("blog", __name__)


@bp.route("/")
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template(
        "index.html",
        all_posts=posts,
        logged_in=current_user.is_authenticated,
        current_user=current_user
    )


@bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    post = BlogPost.query.get_or_404(post_id)
    comments = Comments.query.filter_by(post_id=post_id).all()

    if form.validate_on_submit():

        new_comment = Comments(
            post_id=post_id,
            comment=form.comment.data,
            author=current_user.name,
            author_id=current_user.id
        )

        db.session.add(new_comment)
        db.session.commit()

        return redirect(url_for("blog.show_post", post_id=post_id))

    return render_template(
        "post.html",
        post=post,
        comments=comments,
        form=form,
        logged_in=current_user.is_authenticated,
        current_user=current_user
    )


@bp.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()

    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user.name,
            author_id=current_user.id,
            date=date.today().strftime("%B %d, %Y")
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for("blog.get_all_posts"))

    return render_template("make-post.html", form=form)


@bp.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@edit_and_delete_permission
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    form = CreatePostForm(obj=post)
    usermail = current_user.email

    if form.validate_on_submit():
        form.populate_obj(post)
        db.session.commit()

        return redirect(url_for("blog.show_post", post_id=post.id))

    return render_template("make-post.html", form=form, is_edit=True)


@bp.route("/delete/<int:post_id>")
@edit_and_delete_permission
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    return redirect(url_for("blog.get_all_posts"))
