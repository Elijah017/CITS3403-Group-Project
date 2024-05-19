# CITS3403-Group-Project

## KanBan Board

<b>Purpose</b> The web application is used for project planning. Users are able to register and log in. Afterwards, they are able to create and reply on boards.

##  Members

| UWA Student ID | Name            | GitHub Username|
| :------------- | :-------------- | :------------- |
| 23413154       | Edwin Tang      | Chosdium       |
| 23335907       | Elijah Mullens  | Elijah017      |
| 23365413       | Thomas Morton   | Tommo303       |
| 22939637       | Jiayi Cheng     | JiayiChengdak  |

##  Architecture

This web application utilises server-side rendering with Flask. Each web page is a separate route in the Flask application and each route has its own html file. The app is also linked with a database using WTForms and SQLAlchemy, which stores login and board information.


## Branches

1. <b>main</b>: self-explanatory, the branch where the live working product is stored
2. <b>dev</b>: will be where all experimental changes will be initially merged into and validated. Personal feature branches may spawn off but will be merged into here before any other branch.

## Running the Application

### Initial setup

1. Install dependencies: `pip install -r requirements.txt`
2. Create migration repository: `flask db init`
3. Generate a migration: `flask db migrate`
4. Apply changes described by the migration script: `flask db upgrade`

### Making changes to the database schema

If you make any changes to the database schema, generate a new migration and upgrade the database by repeating steps 3 and 4 above.

### Start the flask server

Run web app: `flask run`

##  Running Tests

Run the Python test files: `python3 test.py`, `python3 SeleniumTest.py`
