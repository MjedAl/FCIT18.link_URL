import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Column, String, Integer, Enum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
import enum
import json

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))

DATABASE_URL = os.getenv('DATABASE_URL') or "sqlite:///{}".format(
os.path.join(project_dir, database_filename))

# https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy()

def setup_db(app, admin, myModelView):
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    Migrate(app, db)
    db.create_all()
    admin.add_view(myModelView(Url, db.session))
    admin.add_view(myModelView(User, db.session))
    admin.add_view(myModelView(Subdomains, db.session))

def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

def random_code():
    code = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(5)])
    while Url.query.filter_by(code=code).first() is not None:
        code = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(5)])
    return code

class categories(enum.Enum):
    IT_Courses = 1
    CS_Courses = 2
    IS_Courses = 3
    Other_Courses = 4
    Shortcuts = 5
    Other = 6
    Semesters = 7

class Url(db.Model):
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, default=random_code, nullable=False)
    fullUrl = Column(String, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)

    def short(self):
        return {
            'id': self.id,
            'code': self.code,
            'fullUrl': self.fullUrl,
            'clicks': self.clicks
        }

    def incrementCounter(self):
        self.clicks= self.clicks+1
        self.update()

    def getFullUrl(self):
        self.incrementCounter()
        return self.fullUrl

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.short())

class Subdomains(db.Model):
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    fullUrl = Column(String, nullable=False)
    clicks = Column(Integer, default=0)
    semester = Column(Integer, default=0)
    category = Column(Enum(categories),nullable=False)

    def short(self):
        return {
            'id': self.id,
            'code': self.code,
            'fullUrl': self.fullUrl,
            'clicks': self.clicks,
            'category': self.category
        }

    def incrementCounter(self):
        self.clicks= self.clicks+1
        self.update()

    def getFullUrl(self):
        self.incrementCounter()
        return self.fullUrl

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.short())

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    password = db.Column(db.String())
    email = db.Column(db.String())
    role = db.Column(db.String())

    def short(self):
        return {
            'fname': self.first_name,
            'lname': self.last_name,
            'email': self.email,
            'id': self.id
        }
    def __repr__(self):
        return json.dumps(self.short())

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def generate_my_password_hash(self, pwd):
        self.password = generate_password_hash(pwd)

    def verify_password(self, pwd):
        if self.password is None:
            return False
        return check_password_hash(self.password, pwd)

    @staticmethod
    def get(user_id):
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def getByEmail(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def getByEmailAndPassword(email, password):
        user = User.getByEmail(email)
        if user is None:
            return None
        else:
            if user.verify_password(password):
                return user
            else:
                return None