# -*- encoding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# app.config.from_object('configuration.ProductionConfig')
app.config.from_object('sprinkler.configuration.DevelopmentConfig')
# app.config.from_object('configuration.TestingConfig')

db = SQLAlchemy(app)  # flask-sqlalchemy

from sprinkler import views, models
