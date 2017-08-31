# -*- coding:utf-8 -*-
__author__ = 'wen'

from os import path


class Config(object):
    SECRET_KEY = 'v2k7QMMNNF5HNghYCCo7ry5fWKs5QBDgG5E6vCfeoK76pEDgxhc6jMN0ylxli531NcVYHi'
    RECAPTCHA_PUBLIC_KEY = '6LcgcS4UAAAAAO0etGgGBcDfCvNGO5_wirtuosX5'
    RECAPTCHA_PRIVATE_KEY = '6LcgcS4UAAAAAP9GMXZsNKW7ozf3l-t1Wj-Yq7ZH'


class ProdConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(path.pardir, 'database.db')
    # SQLALCHEMY_ECHO = True  #显示详细数据库操作
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    print(SQLALCHEMY_DATABASE_URI)
