# -*- encoding: utf-8 -*-

from sprinkler import db
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime, Text, String, Integer


class ModelExample(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(250))
    content = Column(Text)
    date = Column(DateTime)


class User(db.Model):
    id = Column(Integer, primary_key=True)
    user = Column(String(64), unique=True)
    password = Column(String(500))
    name = Column(String(500))
    email = Column(String(120), unique=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % (self.nickname)
