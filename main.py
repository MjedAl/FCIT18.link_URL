# Imports
import json
from flask import Flask, request, render_template, jsonify, abort, redirect, render_template, url_for, flash
from functools import wraps
from db import setup_db, db_drop_and_create_all,  User, Url, Subdomains
# from db import User, Url
from sqlalchemy import desc
import requests
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
import os
from sqlalchemy.sql import func
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
import itertools


class myModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return True
        # TODO: Change to false after implementing login page
        return True 
    def inaccessible_callback(self, name, **kwargs):
        # TODO: redirect to login page
        return redirect(url_for('index'))

# App configuration
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)
admin = Admin(app, name='URLs CONTROL', template_mode='bootstrap3')
setup_db(app, admin, myModelView)

@login_manager.user_loader
def load_user(user_id):
    if user_id is None:
        return None
    return User.query.get(int(user_id))

@app.route('/<code>', methods=['GET'])
def get_url(code):
    url = Url.query.filter_by(code=code).first()
    if url is None:
        abort(404)
    else:
        return redirect(url.getFullUrl(), code=302)

@app.route('/<code>/info', methods=['GET'])
def get_url_info(code):
    url = Url.query.filter_by(code=code).first()
    if url is None:
        abort(404)
    else:
        return jsonify({
            'Success': True,
            'Link_info': url.short()
        })

@app.route("/", subdomain="<subdomain>")
def subdomain_index(subdomain):
    subdomainO = Subdomains.query.filter_by(code=subdomain).one_or_none()
    if subdomainO is none:
        abort(404)
    else:
        return redirect(subdomainO.getFullUrl(), code=302)

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404