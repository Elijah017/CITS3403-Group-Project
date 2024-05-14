from flask import (
    Flask,
    render_template,
    flash,
    redirect,
    request,
    session,
    url_for,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from forms import LoginForm, RegisterForm, BoardForm
from flask_bcrypt import Bcrypt
import json

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)


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
    tickets = db.relationship("Ticket", back_populates="board")


class Permission(db.Model):
    board = db.Column(db.Integer, ForeignKey(Board.id))
    user = db.Column(db.Integer, ForeignKey(User.id))
    writeAccess = db.Column(db.Integer, nullable=False)
    active = db.Column(db.String(20), nullable=False)
    __table_args__ = (PrimaryKeyConstraint("board", "user"),)


class Ticket(db.Model):
    boardId = db.Column(db.Integer, ForeignKey(Board.id))
    creatorId = db.Column(db.Integer, ForeignKey(User.id))
    id = db.Column(db.Integer, nullable=False, default=1)
    type = db.Column(db.Integer, nullable=False, default=0) # 0: Task, 1: Bug, 2: Story
    title = db.Column(db.String, nullable=False, default="New Ticket")
    priority = db.Column(db.Integer, nullable=False, default=1) # 0: Low, 1: Medium, 2: High
    status = db.Column(db.Integer, nullable=False, default=1) # 0: On Hold, 1: To Do, 2: In Progress, 3: Testing, 4: Ready for QA, 5: Done
    description = db.Column(db.String, nullable=False, default="") 
    __table_args__ = (PrimaryKeyConstraint("boardId", "creatorId", "id"),)
    board = db.relationship(Board, back_populates="tickets")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/boards/delete/<int:id>", methods=["DELETE"])
def delete_board(id):
    board = Board.query.filter_by(id=id).first()
    setattr(board, "active", int(False))
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


def AddUser(Uid, Bid, WA, active="active"):  # the mathod to add a user to permission, WA is writeAccess
    board = Board.query.get(Bid)
    if not board:  # check whether the board is exist

        return {"status": "error", "message": "Board not found"}
    user = User.query.get(Uid)
    if not user:  # check whether the user is exist
        return {"status": "error", "message": "User not found"}
    existing_permission = Permission.query.filter_by(board=Bid, user=Uid).first()
    if existing_permission:  # check whether the permission is exist
        return {"status": "error", "message": "Permission already exists"}
    NewPermission = Permission(board=Bid, user=Uid, writeAccess=WA, active=active)
    db.session.add(NewPermission)
    db.session.commit()

    return {"status": "success", "message": "Permission added successfully"}


@app.route("/boards/adduser", methods=["GET", "POST"])
def adduser_by_superuser(BID, Uid, Write_Access):  # this method is to add user by superuser
    Superuser = session["UID"]
    board_id = BID
    add_user_id = Uid
    superuser = Board.query.filter_by(id=BID, superuser=session["UID"]).first()
    if not superuser:
        flash("You are not superuser", "error")

    AddUser(Uid, BID, Write_Access, active="active")
    return redirect(url_for("boards"))


@app.route("/boards/")
def boards():
    render = {}
    user = session["UID"]

    for board in Board.query.filter((Board.superuser == user) | (Board.visibility == "public")):
        owner = get_owner(board.superuser, user)
        if owner == None:
            continue

        render[board.id] = {
            "boardname": board.boardname,
            "owner": owner,
            "active": bool(board.active),
            "visibility": board.visibility,
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
            "active": bool(board.active),
            "visibility": board.visibility,
        }

    return render_template("boards/boards.html", boards=render)


@app.route("/boards/<int:id>", methods=["GET", "POST"])
def board(id):
    if request.method == "GET":
        board = Board.query.filter_by(id=id).first()
        return render_template("boards/board.html", title=board.boardname)
    elif request.method == "POST":
        data = json.loads(request.data)
        ticketId = Ticket.query.filter_by(boardId=int(id), creatorId=int(session["UID"])).count() + 1
        try:
            newTicket = Ticket(
                boardId=int(id),
                creatorId=int(session["UID"]),
                id=ticketId,
                type=data["type"],
                title=data["title"],
                priority=data["priority"],
                status=data["status"],
                description=data["description"]
            )
            db.session.add(newTicket)
            db.session.commit()
            return {"ticketId": ticketId}, 201
        except Exception as e:
            return {"StatusCode": 400}, 400


@app.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    # remember user by session after first login
    if "is_login" in session and session["is_login"]:
        return redirect(url_for("home"))
    if request.method == "POST":  # and form.validate():
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            flash("successfully logged in.", "success")
            session["is_login"] = True  # store a session after login firstly
            session["username"] = user.username  # username is unique
            session["UID"] = user.id
            return redirect(url_for("boards"))
        else:
            flash("Username or Password Incorrect", "danger")
    return render_template("login.html", form=form)


@app.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)  # The detail code from form.py
    if request.method == "POST" and form.validate():
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )  # it will encryption the code in database,  not neccesery

        if User.query.filter_by(email=email).first():
            flash("Email already exists. Please choose another one.", "danger")
            return redirect(url_for("register"))
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("You have successfully registered!", "success")
            return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/newBoard/", methods=["GET", "POST"])
def newBoard():
    form = BoardForm(request.form)
    #   Check whether boardname already exists for superuser
    exist = Board.query.filter_by(boardname=form.boardname.data, superuser=session["UID"]).first()
    if exist:
        flash("Board with this name already exists", "error")
        return render_template("boardCreat.html", form=form)
    #   Posting to db
    if request.method == "POST":
        addboard = Board(
            boardname=form.boardname.data,
            visibility=form.visibility.data,
            superuser=session["UID"],
            active=True,
        )
        db.session.add(addboard)
        db.session.commit()
        if addboard.visibility is True:
            flash("Public Board Created", "success")
        else:
            flash("Private Board Created", "success")
        #   need to return new page?
        return redirect(url_for("boards"))
    return render_template("boardCreat.html", form=form)


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/logout/")
def logout():
    session.clear()
    flash("logged out.", "info")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
