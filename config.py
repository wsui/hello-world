# -*- coding:utf-8 -*-
__author__ = 'wen'


class Config(object):
    pass


class ProdConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///databse.db'
#    SQLALCHEMY_ECHO = True