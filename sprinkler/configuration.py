# -*- encoding: utf-8 -*-

from examples.auth.config import SQLALCHEMY_TRACK_MODIFICATIONS

class Config(object):
    '''
    Configuration base, for all environments.
    '''

    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = "you-will-never-guess"
    CSRF_ENABLED = True


class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
