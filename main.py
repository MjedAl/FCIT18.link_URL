# Imports
import json
from flask import Flask, request, render_template, jsonify, abort, redirect, render_template, url_for, flash, send_from_directory
from db import setup_db, db_drop_and_create_all, User, Url, Subdomains, subClick, urlClick
import requests
from flask_login import (
    LoginManager,
    current_user,
    login_user,
)
import os
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class myAdminView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))


class myUsersView(ModelView):
    column_default_sort = ('clicks', True)

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.role == 'admin' or current_user.role == 'editor':
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))


class AdminIndex(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))


# App configuration
app = Flask(__name__)
app.config['SERVER_NAME'] = 'fcit18.link'
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)
admin = Admin(app, name='FCIT18.link',
              template_mode='bootstrap3', index_view=AdminIndex())
setup_db(app, admin, myAdminView, myUsersView)
captchaPrivateKey = os.environ.get('captchaPrivateKey')


@login_manager.user_loader
def load_user(user_id):
    if user_id is None:
        return None
    return User.query.get(int(user_id))


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        token = request.form['token']
        checkToken = requests.get('https://www.google.com/recaptcha/api/siteverify?secret=' +
                                  captchaPrivateKey+'&response='+token+'&remoteip='+request.remote_addr)
        if checkToken.json()['success']:
            email = request.form["email"]
            password = request.form["password"]
            if email is not None and password is not None:
                user = User.getByEmailAndPassword(email, password)
                if user is None:
                    return jsonify({
                        'success': False,
                        'message': 'Wrong email or password!'
                    })
                else:
                    login_user(user, remember=True)
                    return jsonify({
                        'success': True
                    })
        return jsonify({
            'success': False,
            'message': 'What are you doing?'
        })
    elif request.method == 'GET':
        if current_user.is_authenticated:
            return redirect('/admin', code=302)
        else:
            return render_template('login.html')


@app.route('/')
def index():
    subdomainO = Subdomains.query.filter_by(code='@').one_or_none()
    sub_Click = subClick(SubdomainID=subdomainO.id,
                         userAgent=request.headers.get('User-Agent'))
    sub_Click.insert()
    return redirect(subdomainO.getFullUrl(), code=302)


@app.route('/', subdomain="<subdomain>")
def subdomain_index(subdomain):
    if subdomain.lower() == 'web':
        subdomainO = Subdomains.query.filter_by(code='web').one_or_none()
        subdomainO.incrementCounter()
        sub_Click = subClick(SubdomainID=subdomainO.id,
                             userAgent=request.headers.get('User-Agent'))
        sub_Click.insert()
        return(render_template('index.html'))
    subdomainO = Subdomains.query.filter_by(code=subdomain).one_or_none()
    if subdomainO is None:
        subdomainO = Subdomains.query.filter_by(code='@').one_or_none()
    sub_Click = subClick(SubdomainID=subdomainO.id,
                         userAgent=request.headers.get('User-Agent'))
    sub_Click.insert()
    return redirect(subdomainO.getFullUrl(), code=302)


@app.route('/<code>', methods=['GET'])
def get_url(code):
    url = Url.query.filter_by(code=code).first()
    if url is None:
        subdomainO = Subdomains.query.filter_by(code='@').one_or_none()
        return redirect(subdomainO.getFullUrl(), code=302)
    else:
        url_Click = urlClick(urlID=url.id,
                             userAgent=request.headers.get('User-Agent'))
        url_Click.insert()
        return redirect(url.getFullUrl(), code=302)


@app.route('/favicon.ico')
def f_icon():
    return send_from_directory(os.path.join(app.root_path, 'static/assets/img'),
                               'fcit.jpg', mimetype='image/vnd.microsoft.icon')


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
