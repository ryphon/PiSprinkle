# -*- encoding: utf-8 -*-
import threading

import jinja2
import logging
from aiohttp import web
from RPi import GPIO
import aiohttp_jinja2 as aj
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from sprinkler.configuration import config


if config['DEBUG']:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

app = web.Application(debug=config['DEBUG'])
app.update(config)
aj.setup(app, loader=jinja2.FileSystemLoader('sprinkler/templates'))
SABase = declarative_base()

sa_engine = create_engine(app['SQLALCHEMY_DATABASE_URI'])
session_factory = sessionmaker(bind=sa_engine)
Session = scoped_session(session_factory)
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
    # Stop task scheduler
    sched.shutdown()


async def on_cleanup(app):
    # Clean up GPIO pins
    models.Zone.clean_up_all()


app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)
app.on_cleanup.append(on_cleanup)

app.logger.debug('Main thread: %s', threading.get_ident())
