from flask import Flask, render_template, flash, redirect, request, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.sql import func
from forms import LoginForm, RegisterForm, BoardForm
from flask_bcrypt import Bcrypt
from config import DeploymentConfig
import json

db = SQLAlchemy()


# Refactor app creation function
def create_app(config):
    flaskApp = Flask(__name__)
    flaskApp.config.from_object(config)

    db.init_app(flaskApp)

    return flaskApp


app = create_app(DeploymentConfig)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(200))


class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    boardname = db.Column(db.String(20), nullable=False, unique=True)
    visibility = db.Column(db.String(20))
    superuser = db.Column(db.String(20), ForeignKey(User.id))
    active = db.Column(db.String(20), nullable=False)
    tickets = db.relationship("Ticket", back_populates="board")
    description = db.Column(db.String, nullable=True)


class Permission(db.Model):
    board = db.Column(db.Integer, ForeignKey(Board.id))
    user = db.Column(db.Integer, ForeignKey(User.id))
    writeAccess = db.Column(db.Integer, nullable=False)
    active = db.Column(db.String(20), nullable=False)
    __table_args__ = (PrimaryKeyConstraint("board", "user", name="permission_key"),)


class Ticket(db.Model):
    boardId = db.Column(db.Integer, ForeignKey(Board.id))
    ticketId = db.Column(db.Integer, nullable=False, default=1)
    type = db.Column(db.Integer, nullable=False, default=0)  # 0: Task, 1: Bug, 2: Story
    title = db.Column(db.String, nullable=False, default="New Ticket")
    priority = db.Column(db.Integer, nullable=False, default=1)  # 0: Low, 1: Medium, 2: High
    status = db.Column(db.Integer, nullable=False, default=1)  # 0: On Hold, 1: To Do, 2: In Progress, 3: Testing, 4: Ready for QA, 5: Done
    description = db.Column(db.String, nullable=False, default="")
    __table_args__ = (PrimaryKeyConstraint("boardId", "ticketId", name="ticket_key"),)
    board = db.relationship(Board, back_populates="tickets")


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    boardId = db.Column(db.Integer, ForeignKey(Ticket.boardId))
    ticketId = db.Column(db.Integer, ForeignKey(Ticket.ticketId))
    userId = db.Column(db.Integer, ForeignKey(User.id))
    timestamp = db.Column(db.DateTime, server_default=func.now())
    type = db.Column(db.Integer)
    priority = db.Column(db.Integer)
    status = db.Column(db.Integer)
    comment = db.Column(db.String)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/boards/change_board_state/<int:id>", methods=["PATCH"])
def change_board_state(id):
    board = Board.query.filter_by(id=id).first()
    change_state = request.json["delete"]
    if change_state:
        setattr(board, "active", int(False))
    else:
        setattr(board, "active", int(True))
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


def is_superuser(board_id, user_id):  # check Whether is superuser
    board = Board.query.filter_by(id=board_id, superuser=user_id).first()
    return bool(board)


def AddUser(Uid, Bid, WA, active="active"):  # the mathod to add a user to permission, WA is writeAccess
    board = Board.query.get(Bid)
    if not board:  # check whether the board exists
        return {"status": "error", "message": "Board Not Found"}
    user = User.query.get(Uid)
    if not user:  # check whether the user exists
        return {"status": "error", "message": "User Not Found"}
    existing_permission = Permission.query.filter_by(board=Bid, user=Uid).first()
    if existing_permission:  # check whether the permission exists
        return {"status": "error", "message": "Permission Already Exists"}
    NewPermission = Permission(board=Bid, user=Uid, writeAccess=WA, active=active)
    db.session.add(NewPermission)
    db.session.commit()

    return {"status": "success", "message": "Permission Added Successfully"}


@app.route("/boards/adduser/", methods=["GET", "POST"])
def adduser():
    if request.method == "POST":
        board_id = request.form.get("Bid")
        user_id = request.form.get("Uid")
        write_access = request.form.get("Write_Access")
        uid = session["UID"]
        if is_superuser(board_id, uid) != True:  # check the premission of add user
            flash("NO Permission", "error")
            return redirect(url_for("adduser"))

        # print(board_id,user_id ) just a test
        result = AddUser(user_id, board_id, write_access)
        if result["status"] == "error":
            flash(result["message"], "error")
        else:
            flash(result["message"], "success")
            return redirect(url_for("adduser"))

    return render_template("boards/adduser.html")


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
            "active": board.active,
            "visibility": board.visibility,
            "description": board.description,
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
            "visibility": board.visibility,
            "description": board.description,
        }

    return render_template("boards/boards.html", boards=render)


@app.route("/boards/<int:id>", methods=["GET"])
def board(id):
    if request.method == "GET":
        board = Board.query.filter_by(id=id).first()
        return render_template("boards/board.html", title=board.boardname)


@app.route("/boards/<int:boardId>/tickets", methods=["GET", "POST", "PATCH"])
def tickets(boardId):
    if request.method == "GET":
        tickets = [
            {
                "ticketId": ticket.ticketId,
                "type": ticket.type,
                "title": ticket.title,
                "status": ticket.status,
                "priority": ticket.priority,
                "description": ticket.description,
            }
            for ticket in Ticket.query.filter_by(boardId=boardId)
        ]
        return tickets, 200
    elif request.method == "POST":
        data = json.loads(request.data)
        ticketId = Ticket.query.filter_by(boardId=int(boardId)).count() + 1
        try:
            newTicket = Ticket(
                boardId=int(boardId),
                ticketId=ticketId,
                type=data["type"],
                title=data["title"],
                priority=data["priority"],
                status=data["status"],
                description=data["description"],
            )
            historicalRecord = History(boardId=int(boardId), ticketId=ticketId, userId=session["UID"])
            db.session.add(newTicket)
            db.session.add(historicalRecord)
            db.session.commit()
            return {"ticketId": ticketId}, 201
        except Exception as e:
            print(e)
            return {"StatusCode": 400}, 400
    elif request.method == "PATCH":
        data = json.loads(request.data)
        try:
            oldTicket = Ticket.query.filter_by(boardId=boardId, ticketId=data["ticketId"]).first()
            record = History(
                boardId=int(boardId),
                ticketId=data["ticketId"],
                userId=session["UID"],
                type=None if oldTicket.type == data.get("type") else data.get("type"),
                status=None if oldTicket.status == data.get("status") else data.get("status"),
                priority=None if oldTicket.priority == data.get("priority") else data.get("priority"),
                comment=data.get("comment"),
            )
            Ticket.query.filter_by(boardId=boardId, ticketId=data["ticketId"]).update(
                {
                    Ticket.type: data.get("type", oldTicket.type),
                    Ticket.status: data.get("status", oldTicket.status),
                    Ticket.priority: data.get("priority", oldTicket.priority),
                }
            )

            if record.type is not None or record.status is not None or record.priority is not None or record.comment is not None:
                db.session.add(record)
                db.session.commit()

            return {
                "ticketId": data["ticketId"],
                "title": oldTicket.title,
                "type": data.get("type", oldTicket.type),
                "status": data.get("status", oldTicket.status),
                "priority": data.get("priority", oldTicket.priority),
                "description": oldTicket.description,
            }, 202
        except Exception as e:
            print(e)
            return {"StatusCode": 400}, 400


@app.route("/boards/<int:boardId>/history/<int:ticketId>", methods=["GET"])
def history(boardId, ticketId):
    if request.method == "GET":
        history = [
            {
                "ticketId": record.ticketId,
                "timestamp": record.timestamp,
                "user": User.query.filter_by(id=record.userId).first().username,
                "type": record.type,
                "priority": record.priority,
                "status": record.status,
                "comment": record.comment,
            }
            for record in History.query.filter_by(boardId=boardId, ticketId=ticketId).order_by(History.timestamp)
        ]
        return history, 200


@app.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    # remember user by session after first login
    if "is_login" in session and session["is_login"]:
        return redirect(url_for("home"))
    if request.method == "POST":  # and form.validate()
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            flash("Successfully Logged In", "success")
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

        if User.query.filter_by(email=email).first():  # Check the email if not exist
            flash("Email Already Exists. Please Choose Another One", "danger")
            return redirect(url_for("register"))
        else:  # add user
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("You Have Successfully Registered!", "success")
            return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/newBoard/", methods=["GET", "POST"])
def newBoard():
    form = BoardForm(request.form)
    # Check whether boardname already exists for superuser
    exist = Board.query.filter_by(boardname=form.boardname.data, superuser=session["UID"]).first()
    if exist:
        flash("Board With This Name Already Exists.", "error")
        return render_template("boardCreat.html", form=form)
    # Posting to db
    if request.method == "POST":
        data = json.loads(request.data)
        addboard = Board(
            boardname=data["boardname"],
            visibility=data["visibility"],
            superuser=session["UID"],
            active=True,
            description=data["description"],
        )
        db.session.add(addboard)
        db.session.commit()
        if addboard.visibility is True:
            flash("Public Board Created", "success")
        else:
            flash("Private Board Created", "success")

        return redirect(url_for("boards"))
    return render_template("boardCreat.html", form=form)


def check_user_permission(board_id, user_id):  # Check user permission for one board
    permission = Permission.query.filter_by(board=board_id, user=user_id).first()
    return bool(permission)


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
