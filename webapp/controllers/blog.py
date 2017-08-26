# -*- coding:utf-8 -*-
__author__ = 'wen'

import datetime
from os import path
from sqlalchemy import func
from flask import Flask, g, session, abort, render_template, Blueprint

from webapp.models import db, Post, Tag, Comment, User, tags
from webapp.forms import CommentForm

# 使用蓝图
blog_blueprint = Blueprint(
    'blog',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'blog'),
    url_prefix='/blog'
)


# 侧边栏函数
def sidebar_data():
    recent = Post.query.order_by(
        Post.publish_date.desc()
    ).limit(5).all()
    post_tags = db.session.query(
        Tag, func.count(tags.c.post_id).label('total')
    ).join(
        tags
    ).group_by(Tag).order_by('total DESC').limit(5).all()
    return recent, post_tags


# 截取字符串指定长度
@blog_blueprint.app_template_filter('j_str')
def j_str(s, n):
    if len(s) < n:
        return s
    else:
        return s[:n]


@blog_blueprint.route('/')
@blog_blueprint.route('/<int:page>')
def home(page=1):
    posts = Post.query.order_by(
        Post.publish_date.desc()
    ).paginate(page, 10)
    user = User.query.first()
    recent, top_tags = sidebar_data()
    return render_template(
        'index.html',
        user=user,
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )


@blog_blueprint.route('/post/<int:post_id>', methods=('get', 'post'))
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name = form.name.data
        new_comment.text = form.text.data
        new_comment.post_id = post_id
        new_comment.date = datetime.datetime.now()
        db.session.add(new_comment)
        db.session.commit()
    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent, top_tags = sidebar_data()
    return render_template(
        'post.html',
        user=User.query.get(post.user_id),
        post=post,
        tags=tags,
        comments=comments,
        recent=recent,
        top_tags=top_tags,
        form=form
    )


@blog_blueprint.route('/tag/<string:tag_name>')
def tag(tag_name):
    tag = Tag.query.filter_by(title=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()
    post_users = {}
    for p in posts:
        user = User.query.get(p.user_id)
        post_users[p.id] = user.username
    return render_template(
        'tag.html',
        tag=tag,
        posts=posts,
        recent=recent,
        top_tags=top_tags,
        post_users=post_users
    )


@blog_blueprint.route('/user/<string:username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()
    return render_template(
        'user.html',
        user=user,
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )


@blog_blueprint.route('/restricted')
def admin():
    if g.user is None:
        abort(403)
    return render_template('admin.html')

