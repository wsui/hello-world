# -*- coding:utf-8 -*-
__author__ = 'wen'

from flask import Blueprint, redirect, url_for, render_template, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user
from flask_principal import Identity, AnonymousIdentity, identity_changed
from webapp.forms import LoginForm, RegisterForm, OpenIDForm
from webapp.models import db, User
from webapp.extensions import oid, facebook


main_blueprint = Blueprint(
    'main',
    __name__,
    template_folder='../templates/main'
)


@main_blueprint.route('/')
def index():
    return redirect(url_for('blog.home'))


@main_blueprint.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    form = LoginForm()

    openid_form = OpenIDForm()

    if openid_form.validate_on_submit():
        return oid.try_login(
            openid_form.openid.data,
            ask_for=['nickname', 'email'],
            ask_for_optional=['fullname']
        )

    if form.validate_on_submit():
        user = User.query.filter_by(
            username=form.username.data
        ).one()
        login_user(user, remember=form.remember.data)
        """
        # Add user's name to the cookie
        session['username'] = form.username.data
        """
        identity_changed.send(
            current_app._get_current_object(),
            identity=Identity(user.id)
        )

        flash('You have been logged in.', category='success')
        return redirect(url_for('blog.home'))

    openid_errors = oid.fetch_error()
    if openid_errors:
        flash(openid_errors, category='danger')
    return render_template('login.html', form=form, openid_form=openid_form)


@main_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    """
    # Remove the username from the cookie
    session.pop('username', None)
    """
    identity_changed.send(
        current_app._get_current_object(),
        identity=AnonymousIdentity()
    )
    flash('You have been logged out.', category='success')
    return redirect(url_for('blog.home'))


@main_blueprint.route('/register', methods=['GET', 'POST'])
@oid.loginhandler
def register():
    form = RegisterForm()
    openid_form = OpenIDForm()

    if openid_form.validate_on_submit():
        return oid.try_login(
            openid_form.openid.data,
            ask_for=['nickname', 'email'],
            ask_for_optional=['fullname']
        )

    if form.validate_on_submit():
        new_user = User(form.username.data)
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        flash('Your user have been created, please login.', category='success')

        return redirect(url_for('.login'))

    openid_errors = oid.fetch_error()
    if openid_errors:
        flash(openid_errors, category='danger')

    return render_template('register.html', form=form, openid_form=openid_form)


@main_blueprint.route('/facebook')
def facebook_login():
    return facebook.authorize(
        callback=url_for(
            '.facebook_authorized',
            next=request.referrer or None,
            _external=True
        )
    )


@main_blueprint.route('/facebook/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    session['facebook_oauth_token'] = (resp['access_token'], '')

    me = facebook.get('/me')

    user = User.query.filter_by(
        username=me.data['first_name'] + ' ' + me.data['last_name']
    ).first()

    if not user:
        user = User(me.data['first_name'] + ' ' + me.data['last_name'])
        db.session.add(user)
        db.session.commit()

    flash('You have been logged in.', category='success')

    return redirect(
        request.args.get('next') or url_for('blog.home')
    )