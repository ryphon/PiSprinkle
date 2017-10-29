# -*- encoding: utf-8 -*-

from flask import render_template

from sprinkler import app
from sprinkler.forms import ExampleForm, LoginForm
from sprinkler.models import User
from sprinkler.utils import zones
from werkzeug.utils import redirect
from flask.helpers import url_for


@app.route('/')
def index():
    return render_template('index.html',
                           zones=zones)


@app.route('/view')
def view():
    return render_template('index.html')


@app.route('/zone/toggle/<int:zoneNum>')
def toggle_zone(zoneNum):
    zone = zones[zoneNum-1]
    if zone.is_running():
        zone.stop()
    else:
        zone.run()
    return redirect(url_for('index'))
