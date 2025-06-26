from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField  # ✅ Added TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class LostItemForm(FlaskForm):
    title = StringField('Item Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])  # ✅ This needs the import
    location = StringField('Last Seen Location', validators=[DataRequired()])
    contact_info = StringField('Your Contact Info', validators=[DataRequired()])
    image_file = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Post Item')
