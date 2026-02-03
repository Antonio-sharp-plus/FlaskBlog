from flask_login import UserMixin
from ..extensions import db


class Comments(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    author_id = db.Column(db.Integer, nullable=False)
