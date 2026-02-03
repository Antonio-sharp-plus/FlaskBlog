from flask_login import UserMixin
from ..extensions import db


class BlogPost(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    subtitle = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(80), nullable=False)
    author_id = db.Column(db.Integer, nullable=False)
    img_url = db.Column(db.Text, nullable=False)
