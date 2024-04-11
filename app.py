from flask import Flask, render_template, flash, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegisterForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
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
        user = User.query.filter_by(email=form.email.data).first()#use email to login
        if user and user.password == form.password.data:  
            flash('successfully logged in.', "success")
            session['is_login'] = True #store a session after login firstly
            session['username'] = user.username #username is unique
            print('good')
            return redirect(url_for('home'))
        else:
            flash('Username or Password Incorrect', "danger")
    return render_template('login.html', form=form)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form) #The detail code from form.py 
    if request.method == 'POST' and form.validate():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user: 
            flash(' Email exist', 'danger')
            return redirect(url_for('register'))
        adduser = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data)  
        db.session.add(adduser)
        db.session.commit()
        flash('successfully registered', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout/')
def logout():
    session.clear()
    flash('logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

