CREATE TABLE IF NOT EXISTS "User" (
    id    SERIAL PRIMARY KEY,
    login TEXT   NOT NULL,
    name  TEXT
);

CREATE TABLE IF NOT EXISTS Moderator (
    id INTEGER PRIMARY KEY,

    FOREIGN KEY (id) REFERENCES "User" (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Admin (
    id INTEGER PRIMARY KEY,

    FOREIGN KEY (id) REFERENCES Moderator (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS VerifiedUser (
    id           SERIAL PRIMARY KEY,
    moderator_id INTEGER NOT NULL,
    user_login   TEXT    NOT NULL,

    UNIQUE (moderator_id, user_login),

    FOREIGN KEY (moderator_id) REFERENCES Moderator (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS CreatedPage (
    id       SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL,
    name     TEXT    NOT NULL,

    UNIQUE (admin_id, name),

    FOREIGN KEY (admin_id) REFERENCES Admin (id) ON DELETE CASCADE
);
