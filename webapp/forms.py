# -*- coding:utf-8 -*-
__author__ = 'wen'

from bs4 import BeautifulSoup
from flask_wtf import FlaskForm, RecaptchaField
import wtforms
from wtforms import StringField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, URL
from models import User

# 评论验证
class CommentForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(max=255)]
    )
    text = TextAreaField(u'Comment', validators=[DataRequired()])


# 登录表单
class LoginForm(FlaskForm):
    username = StringField('Username', [
        DataRequired(), Length(max=255)
    ])
    password = PasswordField('Password', [DataRequired()])
    remember = BooleanField('Remember Me')

    def validate(self):
        check_validate = super(LoginForm, self).validate()

        # 如果验证没有通过
        if not check_validate:
            return False

        # 检查是否存在该用户名
        user = User.query.filter_by(
            username=self.username.data
        ).first()
        if not user:
            self.username.errors.append(
                'Invalid username'
            )
            return False

        try:
            # 检查密码是否匹配
            if not user.check_password(self.password.data):
                self.password.errors.append(
                    'Invalid password'
                )
                return False
        except:
            self.password.errors.append(
                'error'
            )
            return False

        return True


# 注册表单
class RegisterForm(FlaskForm):
    username = StringField('Username', [
        DataRequired(),
        Length(max=255, message=u'用户名长度不能大于255'),
        Length(min=6, message=u'用户名长度不能小于6')
    ])
    password = PasswordField('Password', [
        DataRequired(),
        Length(min=8, message=u'密码长度必须大于等于8'),
        Length(max=255, message=u'密码长度不能超过255')
    ])
    confirm = PasswordField('Confirm Password', [
        DataRequired(),
        EqualTo('password', message=u'前后密码不一致')
    ])
    recaptcha = RecaptchaField()

    def validate(self):
        check_validate = super(RegisterForm, self).validate()

        # 如果验证没有通过
        if not check_validate:
            return False

        # 检查是否已存在该用户名
        user = User.query.filter_by(
            username=self.username.data
        ).first()

        if user:
            self.username.errors.append(
                'User with that name already exists'
            )
            return False

        return True


# 写文章表单
class PostForm(FlaskForm):
    # 对文章的长度进行限制
    def Blog_length_limit(form, field):
        soup = BeautifulSoup(field.data, 'html.parser')
        [s.extract() for s in soup('script')]
        length = len(soup.get_text().strip())
        if length < 10:
            raise wtforms.ValidationError(u'文章太短了，多敲几个字吧')
        if length > 20000:
            raise wtforms.ValidationError(u'文章长度超限，不能大于20000')

    title = StringField('Title', [
        DataRequired(),
        Length(max=255)
    ])
    text = TextAreaField('Content', [
        DataRequired(),
        Length(min=6),
        Length(max=100000),
        Blog_length_limit
    ])


# 第三方登录表单
class OpenIDForm(FlaskForm):
    openid = StringField('OpenID URL', [DataRequired(), URL()])