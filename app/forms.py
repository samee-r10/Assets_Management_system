from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class InventoryForm(FlaskForm):
    asset_tag = StringField('Asset Tag', validators=[DataRequired(), Length(max=50)])
    asset_type = SelectField('Asset Type', choices=[], validators=[DataRequired()])
    status = SelectField('Status', choices=[], validators=[DataRequired()])
    brand = SelectField('Brand', choices=[], validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired(), Length(max=50)])
    fa_code = StringField('FA Code', validators=[DataRequired(), Length(max=50)])
    serial_number = StringField('Serial Number', validators=[DataRequired(), Length(max=50)])
    operating_system = SelectField('Operating System', choices=[], validators=[DataRequired()])
    purchase_date = DateField('Purchase Date', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    current_owner = StringField('Current Owner', validators=[DataRequired(), Length(max=50)])
    previous_owner = StringField('Previous Owner', validators=[DataRequired(), Length(max=50)])
    warranty_end_date = DateField('Warranty End Date', validators=[DataRequired()])
    condition_notes = TextAreaField('Condition Notes', validators=[DataRequired(), Length(max=200)])
    department = SelectField('Department', choices=[], validators=[DataRequired()])
    office = SelectField('Office', choices=[], validators=[DataRequired()])
    country = SelectField('Country', choices=[], validators=[DataRequired()])
    vendor_location = SelectField('Vendor Location', choices=[], validators=[DataRequired()])

    # Do not include updated_by in the form

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        
        
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Reset Password')

