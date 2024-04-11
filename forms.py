from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SubmitField
from wtforms.validators import DataRequired, Email, Length
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=256)])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")], render_kw={"placeholder": "Enter your username"})
    email = StringField("Email", validators=[validators.Email(message="Please enter a valid email address")], render_kw={"placeholder": "Enter your email"})
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please Fill This Field"), validators.EqualTo(fieldname="confirm", message="Your Passwords Do Not Match")], render_kw={"placeholder": "Enter your password"})
    confirm = PasswordField("Confirm Password", validators=[validators.DataRequired(message="Please Fill This Field")], render_kw={"placeholder": "Confirm your password"})