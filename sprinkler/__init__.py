# -*- encoding: utf-8 -*-
import jinja2
from aiohttp import web
import aiohttp_jinja2 as aj
from sqlalchemy.ext.declarative import declarative_base

from RPi import GPIO


app = web.Application()
aj.setup(app, loader=jinja2.FileSystemLoader('sprinkler/templates'))
db = declarative_base()
# db = SQLAlchemy(app)  # flask-sqlalchemy

from sprinkler.scheduler import Scheduler  # @IgnorePep8
sched = Scheduler()
from sprinkler import views, models  # @IgnorePep8

GPIO.setmode(GPIO.BCM)
db.create_all()
db.session.commit()
for zone in models.Zone.query.all():
    zone.set_up()
