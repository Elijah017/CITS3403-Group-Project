DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Boards;
DROP TABLE IF EXISTS Permissions;

CREATE TABLE Users(
    ID TEXT PRIMARY KEY,
    UserName TEXT NOT NULL,
    PWD TEXT NOT NULL,
    Email TEXT NOT NULL,
    Active INT
);

CREATE TABLE Boards(
    ID TEXT PRIMARY KEY,
    BoardName TEXT NOT NULL,
    Visibility INT,
    SuperUser TEXT,
    Active INT,
    FOREIGN KEY(SuperUser) REFERENCES Users(ID)
);

CREATE TABLE Permissions(
    Board TEXT,
    User TEXT,
    WriteAccess INT,
    Active INT,
    FOREIGN KEY(Board) REFERENCES Boards(ID),
    FOREIGN KEY(User) REFERENCES Users(ID)
)
