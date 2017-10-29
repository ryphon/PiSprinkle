# -*- encoding: utf-8 -*-

from flask_wtf import Form
from wtforms.fields.simple import TextField, TextAreaField, PasswordField
from wtforms.validators import Required
from wtforms.ext.dateutil.fields import DateTimeField


class ExampleForm(Form):
    title = TextField('Title',
                      validators=[Required()])
    content = TextAreaField('Contents')
    date = DateTimeField('Date', format='%d/%m/%Y %H:%M')


class LoginForm(Form):
    user = TextField('User',
                     validators=[Required()])
    password = PasswordField('Password',
                             validators=[Required()])
