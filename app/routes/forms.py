from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Reset Password')
