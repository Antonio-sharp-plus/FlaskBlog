from datetime import date
import os
import werkzeug
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm, RegisterForm, CommentForm, LoginForm, ForgotForm, ResetForm

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['MAIL_SERVER'] = os.environ.get("MAIL_SERVER")
app.config['MAIL_PORT'] = os.environ.get("MAIL_PORT")
app.config['MAIL_USE_TLS'] = os.environ.get("MAIL_USE_TLS")
app.config['MAIL_USERNAME'] = os.environ.get("mail_username")
app.config['MAIL_PASSWORD'] = os.environ.get("mail_password")
ckeditor = CKEditor(app)
Bootstrap5(app)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# TODO: Configure Flask-Login
loginManager = LoginManager()


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if current_user.id != 1:
            abort(403)
        return function(*args, **kwargs)

    return wrapper


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
loginManager.init_app(app)


# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


class Comments(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, nullable=False)


# TODO: Create a User table for all your registered users. 
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)


with app.app_context():
    db.create_all()


@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        crude_pssw = form.pssw.data
        new_user = User(
            email=form.email.data,
            password=werkzeug.security.generate_password_hash(crude_pssw, method="pbkdf2:sha256", salt_length=8),
            name=form.name.data
        )

        if User.query.filter_by(email=form.email.data).first():
            flash("Email already taken")
            return redirect(url_for("register"))

        if form.email.errors or form.pssw.errors or form.name.errors:
            for error in form.errors.items():
                flash(error)

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html", form=form)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.pssw.data

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("get_all_posts"))
        else:
            flash("Email or password are incorrect")
            return redirect(url_for("login"))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, logged_in=current_user.is_authenticated)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    form = CommentForm()
    requested_post = db.get_or_404(BlogPost, post_id)
    comments = Comments.query.filter_by(post_id=post_id).all()
    if form.validate_on_submit():
        author = current_user.name
        author_id = current_user.id
        comment = form.comment.data

        new_comment = Comments(
            post_id=post_id,
            comment=comment,
            author=author,
            author_id=author_id
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))

    return render_template("post.html", comments=comments, post=requested_post, current_user=current_user, form=form)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_required
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user.name
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_required
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = ForgotForm()
    if request.method == "POST":
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            token = serializer.dumps(current_user.email, salt="password-reset")
            link = url_for("reset_password", token=token, _external=True)

            msg = Message("Reset Password", recipients=[current_user.email])
            msg.body = f"Click here to reset your password:\n{link}"
            mail.send(msg)

            flash(f"You'll receive a link to reset your password at {email}.")
            return redirect(url_for("login"))

        return render_template("forgot_password.html", form=form)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetForm()
    try:
        email = serializer.loads(
            token,
            salt="password-reset",
            max_age=3600  # 1 hora
        )
    except:
        flash("El link es inválido o expiró")
        return redirect(url_for("forgot_password"))

    user = User.query.filter_by(email=email).first()
    if not user:
        abort(404)

    if form.validate_on_submit():
        new_password = form.pssw.data
        user.password = generate_password_hash(new_password)
        db.session.commit()

        flash("Contraseña actualizada correctamente")
        return redirect(url_for("login"))

    return render_template("reset_password.html", form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
