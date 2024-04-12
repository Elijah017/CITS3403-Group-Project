DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Boards;
DROP TABLE IF EXISTS Permissions;

CREATE TABLE Users(
    ID TEXT PRIMARY KEY,
    UserName TEXT NOT NULL,
    PWD TEXT NOT NULL,
    Email TEXT NOT NULL,
    Active INTEGER
);

CREATE TABLE Boards(
    ID TEXT PRIMARY KEY,
    BoardName TEXT NOT NULL,
    Visibility INTEGER,
    SuperUser TEXT,
    Active INTEGER,
    FOREIGN KEY(SuperUser) REFERENCES Users(ID)
);

CREATE TABLE Permissions(
    Board TEXT,
    User TEXT,
    WriteAccess INTEGER,
    Active INTEGER,
    FOREIGN KEY(Board) REFERENCES Boards(ID),
    FOREIGN KEY(User) REFERENCES Users(ID)
)
