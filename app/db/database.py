"""SQLite 连接管理与建表脚本。"""
import sqlite3
from typing import Optional

from app.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS User (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT NOT NULL,
    grade       TEXT NOT NULL DEFAULT '初中',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Word (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    spelling        TEXT NOT NULL UNIQUE,
    phonetic        TEXT DEFAULT '',
    meaning_cn      TEXT NOT NULL,
    pos             TEXT DEFAULT '',
    grade           TEXT NOT NULL DEFAULT '初中',
    confusion_group TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS TestRecord (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    word_id       INTEGER NOT NULL,
    test_type     TEXT NOT NULL,
    user_answer   TEXT DEFAULT '',
    is_correct    INTEGER NOT NULL DEFAULT 0,
    error_type    TEXT NOT NULL DEFAULT 'none',
    edit_distance INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User (id),
    FOREIGN KEY (word_id) REFERENCES Word (id)
);

CREATE TABLE IF NOT EXISTS ErrorBook (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    word_id       INTEGER NOT NULL,
    error_type    TEXT NOT NULL DEFAULT 'none',
    error_count   INTEGER NOT NULL DEFAULT 0,
    resolved      INTEGER NOT NULL DEFAULT 0,
    last_error_at TEXT NOT NULL,
    UNIQUE (user_id, word_id),
    FOREIGN KEY (user_id) REFERENCES User (id),
    FOREIGN KEY (word_id) REFERENCES Word (id)
);

CREATE TABLE IF NOT EXISTS ReviewSchedule (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    word_id         INTEGER NOT NULL,
    repetition      INTEGER NOT NULL DEFAULT 0,
    easiness_factor REAL NOT NULL DEFAULT 2.5,
    interval_days   INTEGER NOT NULL DEFAULT 0,
    next_review_at  TEXT NOT NULL,
    last_review_at  TEXT DEFAULT '',
    status          TEXT NOT NULL DEFAULT 'new',
    UNIQUE (user_id, word_id),
    FOREIGN KEY (user_id) REFERENCES User (id),
    FOREIGN KEY (word_id) REFERENCES Word (id)
);

CREATE INDEX IF NOT EXISTS idx_test_user ON TestRecord (user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_review_due ON ReviewSchedule (user_id, next_review_at);
CREATE INDEX IF NOT EXISTS idx_error_user ON ErrorBook (user_id, resolved);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: Optional[sqlite3.Connection] = None) -> None:
    own = conn is None
    if own:
        conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        if own:
            conn.close()