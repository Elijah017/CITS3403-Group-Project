from flask import Flask, render_template, flash, redirect, request, session, url_for, jsonify
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
    boardname = db.Column(db.String(20), nullable=False,unique=True)
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
    ticketId = db.Column(db.Integer, nullable=False, default=1)
    type = db.Column(db.Integer, nullable=False, default=0)  # 0: Task, 1: Bug, 2: Story
    title = db.Column(db.String, nullable=False, default="New Ticket")
    priority = db.Column(db.Integer, nullable=False, default=1)  # 0: Low, 1: Medium, 2: High
    status = db.Column(db.Integer, nullable=False, default=1)  # 0: On Hold, 1: To Do, 2: In Progress, 3: Testing, 4: Ready for QA, 5: Done
    description = db.Column(db.String, nullable=False, default="")
    __table_args__ = (PrimaryKeyConstraint("boardId", "ticketId"),)
    board = db.relationship(Board, back_populates="tickets")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/boards/change_board_state/<int:id>", methods=["PATCH"])
def change_board_state(id):
    board = Board.query.filter_by(id=id).first()

    change_state = request.json['delete']
    if change_state:
        setattr(board, "active", int(False))
    else:
        setattr(board, 'active', int(True))
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

def is_superuser(board_id, user_id):#check Whether is superuser
    board = Board.query.filter_by(id=board_id, superuser=user_id).first()
    return bool(board)

def AddUser(Uid, Bid, WA, active="active"):  # the mathod to add a user to permission, WA is writeAccess
    board = Board.query.get(Bid)
    if not board:  # check whether the board is exist
        return {"status": "error", "message": "Board Not Found"}
    user = User.query.get(Uid)
    if not user:  # check whether the user is exist
        return {"status": "error", "message": "User Not Found"}
    existing_permission = Permission.query.filter_by(board=Bid, user=Uid).first()
    if existing_permission:  # check whether the permission is exist
        return {"status": "error", "message": "Permission Already Exists"}
    NewPermission = Permission(board=Bid, user=Uid, writeAccess=WA, active=active)
    db.session.add(NewPermission)
    db.session.commit()

    return {"status": "success", "message": "Permission Added Successfully"}



@app.route("/boards/adduser/", methods=["GET", "POST"])
def adduser():
    if request.method=="POST":
        board_id = request.form.get("Bid")
        user_id = request.form.get("Uid")
        write_access = request.form.get("Write_Access")
        uid=session["UID"]
        if is_superuser(board_id, uid)!=True:
             flash("NO Permission", "error")
             return redirect(url_for("adduser"))

        print(board_id,user_id )
        result = AddUser(user_id, board_id, write_access)
        if result["status"] == "error":
            flash(result["message"], "error")
        else:
            flash(result["message"], "success")
            return redirect(url_for("boards"))

    return render_template("boards/adduser.html")

@app.route("/boards/")
def boards():
    render = {}
    user = session["UID"]

    for board in Board.query.filter((Board.superuser == user) | (Board.visibility == "public")):
        owner = get_owner(board.superuser, user)
        if owner == None:
            continue

        render[board.id] = {"boardname": board.boardname, "owner": owner, "active": board.active, "visibility": board.visibility}

    for perm in Permission.query.filter_by(board=user):
        if perm.board in render:
            continue
        board = Board.query.filter_by(id=perm.board)
        owner = get_owner(board.superuser, user)
        if owner == None:
            continue
        render[board.id] = {"boardname": board.boardname, "owner": owner, "active": board.active, "visibility": board.visibility}

    return render_template("boards/boards.html", boards=render)


@app.route("/boards/<int:id>", methods=["GET"])
def board(id):
    if request.method == "GET":
        board = Board.query.filter_by(id=id).first()
        return render_template("boards/board.html", title=board.boardname)


@app.route("/boards/<int:id>/tickets", methods=["GET", "POST", "PATCH"])
def tickets(id):
    if request.method == "GET":
        tickets = [
            {
                "ticketId": ticket.ticketId, 
                "type": ticket.type, 
                "title": ticket.title, 
                "status": ticket.status, 
                "priority": ticket.priority, 
                "description": ticket.description
            } for ticket in Ticket.query.filter_by(boardId=id)
        ]
        return tickets, 200
    elif request.method == "POST":
        data = json.loads(request.data)
        ticketId = Ticket.query.filter_by(boardId=int(id)).count() + 1
        try:
            newTicket = Ticket(
                boardId=int(id),
                creatorId=int(session["UID"]),
                ticketId=ticketId,
                type=data["type"],
                title=data["title"],
                priority=data["priority"],
                status=data["status"],
                description=data["description"],
            )
            db.session.add(newTicket)
            db.session.commit()
            return {"ticketId": ticketId}, 201
        except Exception as e:
            print(e)
            return {"StatusCode": 400}, 400
    elif request.method == "PATCH":
        data = json.loads(request.data)
        try:
            Ticket.query.filter_by(boardId=id, ticketId=data["ticketId"]).update({Ticket.status: data["status"]})
            db.session.commit()
            return {"StatusCode": 202}, 202
        except Exception as e:
            print(e)
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

        if User.query.filter_by(email=email).first():
            flash("Email Already Exists. Please Choose Another One", "danger")
            return redirect(url_for("register"))
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("You Have Successfully Registered!", "success")
            return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/newBoard/", methods=["GET", "POST"])
def newBoard():
    form = BoardForm(request.form)
    #   Check whether boardname already exists for superuser
    exist = Board.query.filter_by(boardname=form.boardname.data, superuser=session["UID"]).first()
    if exist:
        flash("Board With This Name Already Exists.", "error")
        return render_template("boardCreat.html", form=form)
    #   Posting to db
    if request.method == "POST":
        addboard = Board(boardname=form.boardname.data, visibility=form.visibility.data, superuser=session["UID"], active=True)
        db.session.add(addboard)
        db.session.commit()
        if addboard.visibility is True:
            flash("Public Board Created", "success")
        else:
            flash("Private Board Created", "success")

        return redirect(url_for("boards"))
    return render_template("boardCreat.html", form=form)


def check_user_permission(board_id, user_id):
    permission = Permission.query.filter_by(board=board_id, user=user_id).first()
    return bool(permission)

def search_board(board_name):
    board = Board.query.filter_by(boardname=board_name).first()
    return board.id if board else None


@app.route("/boards/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        uid=session["UID"]
        search_query = request.form.get("search_query")
       
        board_id = search_board(search_query)
        if board_id:

            if check_user_permission(board_id, uid):
                return redirect(url_for("board", id=board_id))
            else:
                flash("NO Permission", "error")
            return redirect(url_for("search"))

        else:
            flash("Board not found", "error")
            return redirect(url_for("search"))
    return render_template("boards/search.html")



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
