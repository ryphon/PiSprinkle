# -*- encoding: utf-8 -*-

from flask_wtf import Form
from wtforms.fields.simple import TextField, PasswordField
from wtforms.validators import Required
from wtforms.ext.dateutil.fields import DateField
from wtforms.fields.core import SelectMultipleField, SelectField, FloatField
from wtforms_components.fields.time import TimeField


class ScheduleForm(Form):
    zone = SelectField('Zone',
                       choices=[],
                       validators=[Required()])
    minutes = FloatField('Minutes On',
                         validators=[Required()])
    days = SelectMultipleField('Weekdays',
                               choices=[(0, 'Monday'),
                                        (1, 'Tuesday'),
                                        (2, 'Wednesday'),
                                        (3, 'Thursday'),
                                        (4, 'Friday'),
                                        (5, 'Saturday'),
                                        (6, 'Sunday')])
    time = TimeField('Time',
                     validators=[Required()])
    startDate = DateField('First Day', format='%d/%m/%Y')
    endDate = DateField('Last Day', format='%d/%m/%Y')


class LoginForm(Form):
    user = TextField('User',
                     validators=[Required()])
    password = PasswordField('Password',
                             validators=[Required()])
