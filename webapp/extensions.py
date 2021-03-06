# -*- coding:utf-8 -*-
__author__ = 'wen'

from flask_bcrypt import Bcrypt
from flask_openid import OpenID
from flask import flash, redirect, url_for, session
from flask_oauth import OAuth
from flask_login import LoginManager, AnonymousUserMixin, login_user
from flask_principal import Principal, Permission, RoleNeed

principlals = Principal()
admin_permission = Permission(RoleNeed('admin'))
poster_permission = Permission(RoleNeed('poster'))
default_permission = Permission(RoleNeed('default'))

bcrypt = Bcrypt()
oid = OpenID()
oauth = OAuth()
login_manager = LoginManager()

login_manager.login_view = 'main.login'
login_manager.session_protection = 'strong'
login_manager.login_message = 'Please login to access this page'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    from models import User

    return User.query.get(user_id)


@oid.after_login
def create_or_login(resp):
    # 在函数内导入避免循环导入，model导入了此模块的bcrypt
    from models import db, User

    username = resp.fullname or resp.nickname or resp.email
    if not username:
        flash('Invalid login. Please try again.', 'danger')
        return redirect(url_for('main.login'))

    user = User.query.filer_by(username=username).first()
    if user is None:
        user = User(username)
        db.session.add(user)
        db.session.commit()
    load_user(user.id)
    """
    # 用户登录
    session['username'] = user.username.data
    """
    return redirect(url_for('blog.home'))


facebook = oauth.remote_app(
    'facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key='114768079229706',
    consumer_secret='2740b800deeee5585e072e7be70a3379',
    request_token_params={'scope': 'email'}
)


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_oauth_token')
