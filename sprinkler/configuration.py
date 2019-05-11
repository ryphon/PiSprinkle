# -*- encoding: utf-8 -*-
import os
from uuid import uuid4


class Config(object):
    '''
    Configuration base, for all environments.
    '''

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') \
        or 'sqlite:///app.db'
    REDIS_URI = os.environ.get('REDIS_URI') \
        or 'redis://'
    APSCHEDULE_DATABASE_URI = os.environ.get('APSCHEDULE_DATABASE_URI') \
        or 'sqlite:///jobs.db'
    SECRET_KEY = os.environ.get('SECRET_KEY') \
        or uuid4().hex
    CSRF_ENABLED = True

    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(Config):
    TESTING = True
