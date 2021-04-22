# Imports
import json
from flask import Flask, request, render_template, jsonify, abort, redirect, render_template, url_for, flash
from db import setup_db, db_drop_and_create_all, User, Url, Subdomains
import requests
from flask_login import (
    LoginManager,
    current_user,
    login_user,
)
import os
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView

try:
    from secret import captchaPrivateKey, flask_secret_key
except ModuleNotFoundError:
    captchaPrivateKey = None
    flask_secret_key = None

class myAdminView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return True
        return False 
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))

class myUsersView(ModelView):
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
app.secret_key = os.environ.get("SECRET_KEY") or flask_secret_key or os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)
admin = Admin(app, name='FCIT18.link', template_mode='bootstrap3', index_view=AdminIndex())
setup_db(app, admin, myAdminView, myUsersView)
captchaPrivateKey = os.getenv('captchaPrivateKey') or captchaPrivateKey


@login_manager.user_loader
def load_user(user_id):
    if user_id is None:
        return None
    return User.query.get(int(user_id))

@app.route("/login", methods=['POST','GET'])
def login():
    if request.method == "POST":
        token = request.form['token']
        checkToken = requests.get('https://www.google.com/recaptcha/api/siteverify?secret='+captchaPrivateKey+'&response='+token+'&remoteip='+request.remote_addr)
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
                    return redirect('/admin/', code=302)                    
        return jsonify({
            'success': False,
            'message': 'What are you doing?'
        })
    elif request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        else:
            return render_template('login.html')


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/admin', code=302) 
    else:
        subdomainO = Subdomains.query.filter_by(code='@').one_or_none()
        return redirect(subdomainO.getFullUrl(), code=302)

@app.route('/', subdomain="<subdomain>")
def subdomain_index(subdomain):
    subdomainO = Subdomains.query.filter_by(code=subdomain).one_or_none()
    if subdomainO is None:
        subdomainO = Subdomains.query.filter_by(code='@').one_or_none()
    return redirect(subdomainO.getFullUrl(), code=302)



@app.route('/<code>', methods=['GET'])
def get_url(code):
    url = Url.query.filter_by(code=code).first()
    if url is None:
        abort(404)
    else:
        return redirect(url.getFullUrl(), code=302)

# @app.route('/<code>/info', methods=['GET'])
# def get_url_info(code):
#     url = Url.query.filter_by(code=code).first()
#     if url is None:
#         abort(404)
#     else:
#         return jsonify({
#             'Success': True,
#             'Link_info': url.short()
#         })


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

app.config['SERVER_NAME'] = 'a-fa.sa'
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)