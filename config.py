# -*- coding:utf-8 -*-
__author__ = 'wen'


class Config(object):
    pass


class ProdConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///databse.db'
    # SQLALCHEMY_ECHO = True  #显示详细数据库操作
    SQLALCHEMY_TRACK_MODIFICATIONS = True