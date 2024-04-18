from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SubmitField
from wtforms.validators import DataRequired, Email, Length

def checkPassword(form,field):
    Password=field.data
    if len(Password)<10:
        raise validators.ValidationError("Password length should be more than 10 characters")
    if  not any(char.isdigit() for char in Password):
        raise validators.ValidationError("Password must contain at least one digit")
    if not any(char.islower() for char in Password):
        raise validators.ValidationError("Password must contain at least one lowercase letter")
    if not any(char.isupper() for char in Password):
        raise validators.ValidationError("Password must contain at least one uppercase letter")
    #if not all(char.isalnum() or char in "!@#$%^&*()-_=+{}[]|;:'\",.<>/?`~" for char in Password):
        #raise validators.ValidationError("Password can only contain alphanumeric characters and the following symbols: !@#$%^&*()-_=+{}[]|;:'\",.<>/?`~")
#  we can change the form of password  at this place

#   User login
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)], render_kw={"placeholder" : "Enter Email", "autofocus":True})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=256)], render_kw={"placeholder" : "Enter Password"})
    submit = SubmitField('Login')

#   Registration 
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="length should more than 3")], render_kw={"placeholder": "Enter your username"})
    email = StringField("Email", validators=[validators.Email(message="Invalid email address")], render_kw={"placeholder": "Enter your email"})
    password = PasswordField("Password", validators=[
        validators.DataRequired(message="Password length should be more than 10"),
        checkPassword
    ], render_kw={"placeholder": "Enter your password"})

    confirm = PasswordField("Confirm Password", validators=[
        validators.DataRequired(message="Please fill this field")
    ], render_kw={"placeholder": "Confirm your password"})


#   Board Creation
class BoardForm(FlaskForm):
    name = StringField('Board Name', validators=[validators.DataRequired(message="Board name required"), Length(min=1, max=50)], render_kw={"placeholder": "Enter board name", "autofocus":True}) #  Name of board
    visibility = StringField('Visibility', validators=[validators.DataRequired(
        message="Please enter public or private"), validators.EqualTo('public', 'private')], render_kw={"placeholder": "Enter public or private"})  #  Public or Private
    submit = SubmitField('Create')

#   Permissions 