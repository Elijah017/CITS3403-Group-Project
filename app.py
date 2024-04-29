from flask import Flask, render_template, flash, redirect, request, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from forms import LoginForm, RegisterForm, BoardForm
from flask_bcrypt import Bcrypt
import json

app = Flask(__name__)
app.config.from_file('config.json', load=json.load)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(200))


class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    boardname = db.Column(db.String(20), nullable=False)
    visibility = db.Column(db.String(20))
    superuser = db.Column(db.String(20), ForeignKey(User.id))
    active = db.Column(db.String(20), nullable=False)


class Permission(db.Model):
    board = db.Column(db.Integer, ForeignKey(Board.id))
    user = db.Column(db.Integer, ForeignKey(User.id))
    writeAccess = db.Column(db.Integer, nullable=False)
    active = db.Column(db.String(20), nullable=False)
    __table_args__ = (PrimaryKeyConstraint('board', 'user'),)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/boards/delete/<int:id>', methods=['DELETE'])
def delete_board(id):
    board = Board.query.filter_by(id=id).first()
    setattr(board, 'active', int(False))
    db.session.commit()
    return jsonify(success=True)


def get_owner(id, user):
    if int(id) == user:
        return "Me"
    else:
        username = User.query.filter_by(id=id).first()
        if username == None:
            return None
        return username.username


@app.route('/boards/')
def boards():
    render = {}
    user = session['UID']

    for board in Board.query.filter(
        (Board.superuser == user) | (Board.visibility == "public")
    ):
        owner = get_owner(board.superuser, user)
        if owner == None:
            continue

        render[board.id] = {
            "boardname": board.boardname,
            "owner": owner,
            "active": board.active,
            "visibility": board.visibility
        }

    for perm in Permission.query.filter_by(board=user):
        if perm.board in render:
            continue
        board = Board.query.filter_by(id=perm.board)
        owner = get_owner(board.superuser, user)
        if owner == None:
            continue
        render[board.id] = {
            "boardname": board.boardname,
            "owner": owner,
            "active": board.active,
            "visibility": board.visibility
        }

    return render_template('boards/boards.html', boards=render)


@app.route('/boards/<int:id>', methods=['GET', 'POST'])
def board(id):
    board = Board.query.filter_by(id=id).first()
    return render_template('boards/board.html', title=board.boardname)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    # remember user by session after first login
    if "is_login" in session and session['is_login']:
        return redirect(url_for('home'))
    if request.method == 'POST':  # and form.validate():
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            flash('successfully logged in.', "success")
            session['is_login'] = True  # store a session after login firstly
            session['username'] = user.username  # username is unique
            session['UID'] = user.id
            return redirect(url_for('boards'))
        else:
            flash('Username or Password Incorrect', "danger")
    return render_template('login.html', form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)  # The detail code from form.py
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data).decode(
            'utf-8')  # it will encryption the code in database,  not neccesery

        if User.query.filter_by(email=email).first():
            flash('Email already exists. Please choose another one.', 'danger')
            return redirect(url_for('register'))
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('You have successfully registered!', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/newBoard/', methods=['GET', 'POST'])
def newBoard():
    form = BoardForm(request.form) 
    #   Check whether boardname already exists for superuser
    exist = Board.query.filter_by(boardname=form.boardname.data, superuser=session['UID']).first()
    if exist:
        flash('Board with this name already exists', 'error')
        return render_template('boardCreat.html', form=form)
    #   Posting to db
    if request.method == 'POST':
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
        return redirect(url_for('boards'))
    return render_template('boardCreat.html', form=form)

@app.route('/logout/')
def logout():
    session.clear()
    flash('logged out.', 'info')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
