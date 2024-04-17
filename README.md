# CITS3403-Group-Project

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
