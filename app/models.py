import warnings
warnings.simplefilter("ignore")
from flask_login import UserMixin

from app import db, login_manager

class im_data(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url_name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    url = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.TIMESTAMP, nullable=False)
    update_time = db.Column(db.TIMESTAMP, nullable=False)
    user_id = db.Column(db.String(100), index=True, nullable=False)
    share = db.Column(db.Boolean, index=True, nullable=False)
    hits = db.Column(db.Integer, index=True, default=0)

    def __repr__(self):
        return '<URL %r>' % (self.url_name)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=False)
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime)

    def __repr__(self):
        return '<User %r' % (self.email)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
