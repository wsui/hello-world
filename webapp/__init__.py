# -*- coding:utf-8 -*-
__author__ = 'wen'

from flask import Flask, redirect, url_for, render_template
from config import DevConfig
from flask.views import View

from models import db
from controllers.blog import blog_blueprint


def create_app(objecrt_name):
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    db.init_app(app)

    # 根目录重定向到蓝图
    @app.route('/')
    def index():
        return redirect(url_for('blog.home'))


    app.add_url_rule(
        '/', view_func=GenericView.as_view(
            'home', template='home.html'
        )
    )

    # 自定义错误404页面
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('page_not_found.html'), 404

    app.register_blueprint(blog_blueprint)
    return app


# 视图函数
class GenericView(View):
    methods = ['GET', 'POST']

    def __init__(self, template):
        self.template = template
        super(GenericView, self).__init__()

    def dispatch_request(self):
        return render_template(self.template)

"""
if __name__ == '__main__':
    app.run()
"""