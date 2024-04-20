from flask import Flask, render_template, flash, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from forms import LoginForm, RegisterForm, BoardForm
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['SECRET_KEY'] = '123456789'#Cross-Site Request Forgery


db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

<<<<<<< HEAD

=======
#   User Table
>>>>>>> bb2e3f4 (Added board and permission tables classes and started constructing database links)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(200))  

@app.route("/")
=======
#   Board Table
class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    boardname = db.Column(db.String(20), nullable=False)
    visibility = db.Column(db.String(20))
    superuser = db.Column(db.String(20), ForeignKey(User.id))
    active = db.Column(db.String(20), nullable=False)

#   Permissions Table
class Permission(db.Model):
    board = db.Column(db.Integer, ForeignKey(Board.id))
    user = db.Column(db.Integer, ForeignKey(User.id))
    writeAccess = db.Column(db.Integer, nullable=False)
    active = db.Column(db.String(20), nullable=False)
    __table_args__ = (PrimaryKeyConstraint('board', 'user'),)

@app.route('/')
>>>>>>> bb2e3f4 (Added board and permission tables classes and started constructing database links)
def home():
    return render_template("index.html")



@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if "is_login" in session and session['is_login']:# remember user by session after first login
        return redirect(url_for('home'))
    if request.method == 'POST' and form.validate():
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):  
            flash('successfully logged in.', "success")
            session['is_login'] = True #store a session after login firstly
            session['username'] = user.username #username is unique
            session['UID'] = user.id
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
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')# it will encryption the code in database,  not neccesery 
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another one.', 'danger')
            return redirect(url_for('register'))
        elif User.query.filter_by(email=email).first():
            flash('Email already exists. Please choose another one.', 'danger')
            return redirect(url_for('register'))
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("You have successfully registered!", "success")
            return redirect(url_for("login"))

    return render_template('register.html', form=form)


@app.route('/newBoard/', methods=['GET', 'POST'])
def newBoard():
    form = BoardForm(request.form)  #   Get the form

    if request.method == 'POST': # and form.validate():
        addboard = Board(
            boardname=form.boardname.data,
            visibility=form.visibility.data,
            superuser=session['UID'],
            active=True
        )
        db.session.add(addboard)
        db.session.commit()
        if addboard.visibility is True:
            flash('Public Board Created', 'success')
        else:
            flash('Private Board Created', 'success')
        #   need to return new page? 
        return redirect(url_for('home'))
    return render_template('boardCreat.html', form=form)

<<<<<<< HEAD
@app.route("/logout/")
=======

@app.route('/logout/')
>>>>>>> bb2e3f4 (Added board and permission tables classes and started constructing database links)
def logout():
    session.clear()
    flash("logged out.", "info")
    return redirect(url_for("home"))



if __name__ == '__main__':
    app.run(debug=True)
