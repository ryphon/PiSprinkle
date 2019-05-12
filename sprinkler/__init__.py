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

sa_engine = create_engine(app.config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=sa_engine)
db = Session()

from sprinkler.scheduler import Scheduler  # @IgnorePep8
sched = Scheduler()
from sprinkler import views, models  # @IgnorePep8


async def on_startup(app):
    # Set up db if necessary
    SABase.metadata.create_all(sa_engine, checkfirst=True)

    # Set up GPIO pins
    GPIO.setmode(GPIO.BCM)
    db.commit()
    for zone in db.query(models.Zone).all():  # models.Zone.query.all():
        zone.set_up()

    # Start up task scheduler
    sched.start()


async def on_shutdown(app):
    # Clean up GPIO pins
    models.Zone.clean_up_all()

    # Stop task scheduler
    sched.shutdown()


app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)
