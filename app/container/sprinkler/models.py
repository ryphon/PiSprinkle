# -*- encoding: utf-8 -*-

from sprinkler import app, SABase
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String, Integer
from sqlalchemy import event
from RPi import GPIO


class Zone(SABase):
    """ Represents an irrigation zone assigned to a GPIO pin """
    __tablename__ = 'zone'

    endpoint = 'zone'

    id = Column(Integer, primary_key=True)
    pin = Column(Integer, unique=True)
    name = Column(String(64), unique=True)

    def __init__(self, pin: int, name: str):
        app.logger.info('--- Zone init ---')
        self.pin = pin
        self.name = name
        self.set_up()

    @property
    def state(self):
        return 'on' if GPIO.HIGH == GPIO.input(self.pin) else 'off'

    @property
    def uri(self):
        return str(app.router[self.endpoint].url_for(id=str(self.id)))

    @state.setter
    def state(self, state):
        if state is True or state == 'on':
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)

    @property
    def as_dict(self):
        return {
            'uri': self.uri,
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'pin': self.pin
        }

    def set_up(self):
        app.logger.info('Setting up {}'.format(self))
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)

    def clean_up(self, force=False):
        app.logger.info('Cleaning up {}'.format(self))
        from sprinkler import db

        cls = self.__class__
        dup_zone = db.query(cls).filter(cls.id != self.id).filter(cls.pin == self.pin)
        # Protection for clean_up on duplicate zone creation failure
        if force or not dup_zone:
            GPIO.output(self.pin, GPIO.LOW)
            GPIO.setup(self.pin, GPIO.IN)
            # This sometimes triggers a warning even though the 'channel' is
            # in fact set up. Why? Haven't figured that out yet.
            GPIO.cleanup(self.pin)

    @classmethod
    def clean_up_all(cls):
        from sprinkler import db

        zones = db.query(cls).all()
        for zone in zones:
            zone.clean_up(force=True)

    def __repr__(self):
        return '<Zone(id={id}, name={name}, pin={pin})>'.format(
            id=self.id,
            name=self.name,
            pin=self.pin)


@event.listens_for(Zone, 'after_delete')
def delete_zone_handler(mapper, connection, target):
    """ Just to keep GPIO pins configured appropriately """
    app.logger.info('after_delete')
    target.clean_up()
