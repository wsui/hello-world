# -*- coding:utf-8 -*-
__author__ = 'wen'

from  flask import Flask
from config import DevConfig
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)


class User(db.Model):
#    __tablename__ = 'user_table_name'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column('user_name', db.String(255))
    password = db.Column('password', db.String(255))
'''
    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<User "{}">'.format(self.username)
'''

@app.route('/')
def hello_world():
    return '<h1>hello world!</h1><script>alert("hello world!");</script>'


if __name__ == '__main__':
    app.run()