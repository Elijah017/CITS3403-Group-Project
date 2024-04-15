from flask import Flask, render_template, flash, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegisterForm
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance\\database.db'

app.config['SECRET_KEY'] = '123456789'#Cross-Site Request Forgery


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(200))  

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if "is_login" in session and session['is_login']:# remember user by session after first login
        return redirect(url_for('home'))
    if request.method == 'POST' and form.validate():
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and Bcrypt.check_password_hash(user.password, password):  
            flash('successfully logged in.', "success")
            session['is_login'] = True #store a session after login firstly
            session['username'] = user.username #username is unique
            
            return redirect(url_for('home'))
        else:
            flash('Username or Password Incorrect', "danger")
    return render_template('login.html', form=form)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form) #The detail code from form.py 
    if request.method == 'POST' and form.validate():
        username=form.username.data
        email= form.email.data
        password = Bcrypt.generate_password_hash(form.password.data).decode('utf-8')# it will encryption the code in database,  not neccesery 
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please choose another one.', 'danger')
            return redirect(url_for('register'))
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('You have successfully registered!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/logout/')
def logout():
    session.clear()
    flash('logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

