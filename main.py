# -*- coding:utf-8 -*-
__author__ = 'wen'

from flask import Flask, g, session, abort, render_template, Blueprint, redirect, url_for
from config import DevConfig
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask.views import View
import datetime

app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)

# 用户信息
class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column('user_name', db.String(255))
    password = db.Column('password', db.String(255))
    posts = db.relationship(
        'Post',
        backref='user',
        lazy='dynamic'
    )

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<User "{},{},{}">'.format(self.username, self.id, self.password)

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


# 评论验证
class CommentForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(max=255)]
    )
    text = TextAreaField(u'Comment', validators=[DataRequired()])

# 使用蓝图
blog_blueprint = Blueprint(
    'blog',
    __name__,
    template_folder='templates/blog',
    url_prefix='/blog'
)

# 根目录重定向到蓝图
@app.route('/')
def index():
    return redirect(url_for('blog.home'))


# 截取字符串指定长度
@app.template_filter('j_str')
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


# 检查session变量是否带有用户信息
@app.before_request
def before_request():
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@blog_blueprint.route('/restricted')
def admin():
    if g.user is None:
        abort(403)
    return render_template('admin.html')


# 自定义错误404页面
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


# 视图函数
class GenericView(View):
    methods = ['GET', 'POST']

    def __init__(self, template):
        self.template = template
        super(GenericView, self).__init__()

    def dispatch_request(self):
        return render_template(self.template)


app.add_url_rule(
    '/', view_func=GenericView.as_view(
        'home', template='home.html'
    )
)

app.register_blueprint(blog_blueprint)
if __name__ == '__main__':
    app.run()