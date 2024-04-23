from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

def checkPassword(form,field):
    """
    Defines password validation parameters. These parameters are:
        - length >= 10
        - atleast 1 digit
        - atleast 1 lowercase
        - atleast 1 uppercase
    """
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

class LoginForm(FlaskForm):
    email = StringField(
        'Email', 
        validators=[DataRequired(), Email(), Length(max=50)],
        render_kw={
            "class": "lowered",
            "placeholder" : "Enter Email", 
            "autofocus":True
        }
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=256)],
        render_kw={
            "class": "lowered",
            "placeholder" : "Enter Password"
        }
    )

class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[validators.Length(min=3, max=25),
        validators.DataRequired(message="length should more than 3")],
        render_kw={
            "class": "lowered",
            "placeholder": "Enter your username",
            "autofocus": True
        }
    )
    email = StringField(
        "Email",
        validators=[validators.Email(message="Invalid email address")],
        render_kw={
            "class": "form-control",
            "placeholder": "Enter your email"
            }
        )
    password = PasswordField(
        "Password",
        validators=[
            validators.DataRequired(message="Password length should be more than 10"),
            checkPassword
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Enter your password"
            }
        )

    confirm = PasswordField(
        "Confirm Password",
        validators=[
            validators.DataRequired(message="Please fill this field")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Confirm your password"
            }
        )


class BoardForm(FlaskForm):
    boardname = StringField('Board Name',
        validators=[validators.DataRequired(message="Board name required"),
        Length(min=1, max=50)],
        render_kw={
            "class": "form-control",
            "placeholder": "Board Name",
            "autofocus":True
        }
    )
    visibility = SelectField('Visibility',
        choices=[
            ('public', 'Public'),
            ('private', 'Private')
        ],
        render_kw={
            "class": "form-select"
        }
    )
    submit = SubmitField('Create',
        render_kw={
            "class": "btn btn-primary"
        }
    )
    supervisor = StringField('Superuser')
    active = SelectField('active')

class Permission(FlaskForm):
    board = StringField()
    user = StringField()
    writeAccess = StringField('')

