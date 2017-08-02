# -*- coding:utf-8 -*-
__author__ = 'wen'


class Config(object):
    SECRET_KEY = 'v2k7QMMNNF5HNghYCCo7ry5fWKs5QBDgG5E6vCfeoK76pEDgxhc6jMN0ylxli531NcVYHi'


class ProdConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///databse.db'
    # SQLALCHEMY_ECHO = True  #显示详细数据库操作
    SQLALCHEMY_TRACK_MODIFICATIONS = True
