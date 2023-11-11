from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError


class UniversityForm(FlaskForm):
    universityName = StringField(label='University Name or Abbriv.', validators=[DataRequired()])
    submit = SubmitField(label='Search')


class emailForm(FlaskForm):
    email = StringField(label='Email Address', validators=[DataRequired()])
    submit = SubmitField(label='Submit')