# -*- encoding: utf-8 -*-
import jinja2
import logging
from aiohttp import web
import aiohttp_jinja2 as aj
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from RPi import GPIO
from sqlalchemy.orm import sessionmaker

from sprinkler.configuration import DevelopmentConfig as Config

logging.basicConfig(level=logging.DEBUG)

app = web.Application(debug=Config.DEBUG)
app.config = Config
aj.setup(app, loader=jinja2.FileSystemLoader('sprinkler/templates'))
SABase = declarative_base()
# db = SQLAlchemy(app)  # flask-sqlalchemy

sa_engine = create_engine(app.config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=sa_engine)
db = Session()

from sprinkler.scheduler import Scheduler  # @IgnorePep8
sched = Scheduler()
from sprinkler import views, models  # @IgnorePep8

SABase.metadata.create_all(sa_engine, checkfirst=True)

GPIO.setmode(GPIO.BCM)
db.commit()
for zone in db.query(models.Zone).all():  # models.Zone.query.all():
    zone.set_up()
