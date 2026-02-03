from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap5


db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
ckeditor = CKEditor()
bootstrap = Bootstrap5()
