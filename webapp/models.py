# -*- coding:utf-8 -*-
__author__ = 'wen'

from flask_sqlalchemy import SQLAlchemy
from webapp.extensions import bcrypt, login_manager
from flask_login import AnonymousUserMixin, UserMixin

db = SQLAlchemy()


class AnonymousUser(AnonymousUserMixin):
    # confirmed = False
    @property
    def is_authenticated(self):
        return False


login_manager.anonymous_user = AnonymousUser

roles = db.Table(
    'role_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

# 用户信息
class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column('user_name', db.String(255), unique=True)
    password = db.Column('password', db.String(255))
    posts = db.relationship(
        'Post',
        backref='user',
        lazy='dynamic'
    )

    roles = db.relationship(
        'Role',
        secondary=roles,
        backref=db.backref('users', lazy='dynamic')
    )

    def __init__(self, username):
        self.username = username
        default = Role.query.filter(name='default').one()
        self.roles.append(default)

    def __repr__(self):
        return '<User "{},{},{}">'.format(self.username, self.id, self.password)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def is_authenticated(self):
        if isinstance(self, AnonymousUser):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_annoymous(self):
        if isinstance(self, AnonymousUser):
            return True
        else:
            return False

    def get_id(self):
        return unicode(self.id)


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role {}>'.format(self.name)

# 标签
tags = db.Table('post_tags',
                db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                )

# 文章信息
class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    publish_date = db.Column(db.DateTime())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic'
    )
    tags = db.relationship(
        'Tag',
        secondary=tags,
        backref=db.backref('posts', lazy='dynamic')
    )

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return '<Post "{},{},{},{},{}">'.format(self.title, self.id, self.user_id, self.publish_date, self.text)


# 标签
class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return '<Tag "{}">'.format(self.title)


# 评论信息
class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    text = db.Column(db.Text())
    date = db.Column(db.DateTime())
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))

    def __repr__(self):
        return '<Comment "{}">'.format(self.text[:15])



