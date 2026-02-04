from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer

from app.extensions import db, mail
from app.models import User
from forms import LoginForm, RegisterForm, ForgotForm, ResetForm
from flask_mail import Message
from flask import current_app

bp = Blueprint("auth", __name__)


def get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


# Auth Routes


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already taken")
            return redirect(url_for("auth.register"))

        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=generate_password_hash(form.pssw.data, method="pbkdf2:sha256", salt_length=8)
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("blog.get_all_posts"))

    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user or not check_password_hash(user.password, form.pssw.data):
            flash("Invalid email or password")
            return redirect(url_for("auth.login"))

        login_user(user)
        return redirect(url_for("blog.get_all_posts"))

    return render_template("login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("blog.get_all_posts"))


# Password Reset

@bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    form = ForgotForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("If that email exists, a reset link will be sent.")
            return redirect(url_for("auth.login"))

        token = get_serializer().dumps(user.email, salt="password-reset")
        link = url_for("auth.reset_password", token=token, _external=True)

        msg = Message(
            sender="antonicoa2014@gmail.com",
            subject="Reset Password",
            recipients=[user.email],
            body=f"Click here to reset your password:\n{link}"
        )

        mail.send(msg)
        flash("Password reset email sent.")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html", form=form)


@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetForm()

    try:
        email = get_serializer().loads(
            token,
            salt="password-reset",
            max_age=3600
        )
    except:
        flash("Invalid or expired link")
        return redirect(url_for("auth.forgot"))

    user = User.query.filter_by(email=email).first_or_404()

    if form.validate_on_submit():
        user.password = generate_password_hash(
            form.pssw.data, method="pbkdf2:sha256", salt_length=8
        )
        db.session.commit()

        flash("Password updated successfully")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", form=form)
