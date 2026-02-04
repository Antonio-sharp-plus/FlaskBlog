import os
from flask import Flask
from dotenv import load_dotenv
from .extensions import db, login_manager, mail, ckeditor, bootstrap


def init_db(app):
    with app.app_context():
        db.create_all()

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    init_db(app)
    login_manager.init_app(app)
    mail.init_app(app)
    ckeditor.init_app(app)
    bootstrap.init_app(app)

    # IMPORTANT: Import models so user_loader can see User
    from . import models

    from .routes import auth, blog, pages
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(pages.bp)

    return app
