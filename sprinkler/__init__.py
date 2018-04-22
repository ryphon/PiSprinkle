# -*- encoding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
import sys
from flask_restful import Api
from flask.app import Flask
from RPi import GPIO


app = Flask(__name__)
api = Api(app)

app.config.from_object('configuration.ProductionConfig')
# app.config.from_object('sprinkler.configuration.DevelopmentConfig')
# app.config.from_object('configuration.TestingConfig')

db = SQLAlchemy(app)  # flask-sqlalchemy


from sprinkler.schedule import Scheduler  # @IgnorePep8
sched = Scheduler()
from sprinkler import views, models  # @IgnorePep8


GPIO.setmode(GPIO.BCM)
db.create_all()
db.session.commit()
for zone in models.Zone.query.all():
    zone.set_up()
