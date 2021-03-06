from datetime import datetime
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
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DATABASE_URL = os.getenv('DATABASE_URL')

# https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy()


def setup_db(app, admin, myAdminView, myUsersView):
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    Migrate(app, db)
    db.create_all()
    admin.add_view(myUsersView(Url, db.session))
    admin.add_view(myUsersView(Subdomains, db.session))
    admin.add_view(myAdminView(User, db.session))


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


def random_code():
    code = ''.join([random.choice(string.ascii_letters + string.digits)
                    for n in range(5)])
    while Url.query.filter_by(code=code).first() is not None:
        code = ''.join(
            [random.choice(string.ascii_letters + string.digits) for n in range(5)])
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
    ClicksT = db.relationship("urlClick")

    def short(self):
        return {
            'id': self.id,
            'code': self.code,
            'fullUrl': self.fullUrl,
            'clicks': self.clicks
        }

    def incrementCounter(self):
        self.clicks = self.clicks+1
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
    category = Column(Enum(categories), nullable=False)
    ClicksT = db.relationship("subClick")

    def short(self):
        return {
            'id': self.id,
            'code': self.code,
            'fullUrl': self.fullUrl,
            'clicks': self.clicks,
            'category': self.category
        }

    def incrementCounter(self):
        self.clicks = self.clicks+1
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


class subClick(db.Model):
    id = Column(Integer, primary_key=True)
    userAgent = db.Column(db.String)
    ip = db.Column(db.String)
    SubdomainID = db.Column(db.Integer, db.ForeignKey('subdomains.id'), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class urlClick(db.Model):
    id = Column(Integer, primary_key=True)
    userAgent = db.Column(db.String)
    ip = db.Column(db.String)
    urlID = db.Column(db.Integer, db.ForeignKey('url.id'), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow , nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    password = db.Column(db.String())
    email = db.Column(db.String())
    role = db.Column(db.String())
    lastSeen = db.Column(db.DateTime, default=datetime.utcnow)

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
