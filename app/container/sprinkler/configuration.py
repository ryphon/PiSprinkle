# -*- encoding: utf-8 -*-
import os


config = {
    'SQLALCHEMY_DATABASE_URI': os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///app.db',
    'APSCHEDULE_DATABASE_URI': os.environ.get('APSCHEDULE_DATABASE_URI') or 'sqlite:///jobs.db',
    'DEBUG': os.environ.get('DEBUG', '').lower() == 'true',
    'TESTING': os.environ.get('TESTING', '').lower() == 'true',
    'SQLALCHEMY_TRACK_MODIFICATIONS': os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', '').lower() == 'true'
}
