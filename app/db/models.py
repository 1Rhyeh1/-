"""数据访问对象（DAO），封装各表的常用读写操作。"""
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.db.database import get_connection


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class UserDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_or_create(self, username: str, grade: str = "初中") -> int:
        row = self.conn.execute(
            "SELECT id FROM User WHERE username = ?", (username,)
        ).fetchone()
        if row:
            return row["id"]
        cur = self.conn.execute(
            "INSERT INTO User (username, grade, created_at) VALUES (?, ?, ?)",
            (username, grade, _now()),
        )
        self.conn.commit()
        return cur.lastrowid

    def get(self, user_id: int) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM User WHERE id = ?", (user_id,)
        ).fetchone()


class WordDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) AS c FROM Word").fetchone()["c"]

    def add(self, spelling: str, meaning_cn: str, phonetic: str = "",
            pos: str = "", grade: str = "初中", confusion_group: str = "") -> int:
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO Word "
            "(spelling, phonetic, meaning_cn, pos, grade, confusion_group) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (spelling, phonetic, meaning_cn, pos, grade, confusion_group),
        )
        self.conn.commit()
        return cur.lastrowid

    def get(self, word_id: int) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM Word WHERE id = ?", (word_id,)
        ).fetchone()

    def by_spelling(self, spelling: str) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM Word WHERE LOWER(spelling) = LOWER(?)", (spelling,)
        ).fetchone()

    def all(self, grade: Optional[str] = None) -> List[sqlite3.Row]:
        if grade:
            return self.conn.execute(
                "SELECT * FROM Word WHERE grade = ? ORDER BY spelling", (grade,)
            ).fetchall()
        return self.conn.execute("SELECT * FROM Word ORDER BY spelling").fetchall()

    def confusion_words(self, word_id: int) -> List[str]:
        """返回同形近词组的其他单词拼写。"""
        row = self.get(word_id)
        if not row or not row["confusion_group"]:
            return []
        rows = self.conn.execute(
            "SELECT spelling FROM Word WHERE confusion_group = ? AND id != ?",
            (row["confusion_group"], word_id),
        ).fetchall()
        return [r["spelling"] for r in rows]


class TestRecordDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, user_id: int, word_id: int, test_type: str, user_answer: str,
            is_correct: bool, error_type: str = "none", edit_distance: int = 0) -> int:
        cur = self.conn.execute(
            "INSERT INTO TestRecord "
            "(user_id, word_id, test_type, user_answer, is_correct, error_type, edit_distance, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, word_id, test_type, user_answer, int(is_correct),
             error_type, edit_distance, _now()),
        )
        self.conn.commit()
        return cur.lastrowid

    def stats(self, user_id: int) -> Dict[str, Any]:
        total = self.conn.execute(
            "SELECT COUNT(*) AS c FROM TestRecord WHERE user_id = ?", (user_id,)
        ).fetchone()["c"]
        correct = self.conn.execute(
            "SELECT COUNT(*) AS c FROM TestRecord WHERE user_id = ? AND is_correct = 1",
            (user_id,),
        ).fetchone()["c"]
        return {"total": total, "correct": correct,
                "accuracy": (correct / total) if total else 0.0}

    def error_type_distribution(self, user_id: int) -> Dict[str, int]:
        rows = self.conn.execute(
            "SELECT error_type, COUNT(*) AS c FROM TestRecord "
            "WHERE user_id = ? AND is_correct = 0 GROUP BY error_type",
            (user_id,),
        ).fetchall()
        return {r["error_type"]: r["c"] for r in rows}


class ErrorBookDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def upsert_error(self, user_id: int, word_id: int, error_type: str) -> None:
        row = self.conn.execute(
            "SELECT id, error_count FROM ErrorBook WHERE user_id = ? AND word_id = ?",
            (user_id, word_id),
        ).fetchone()
        if row:
            self.conn.execute(
                "UPDATE ErrorBook SET error_count = error_count + 1, error_type = ?, "
                "resolved = 0, last_error_at = ? WHERE id = ?",
                (error_type, _now(), row["id"]),
            )
        else:
            self.conn.execute(
                "INSERT INTO ErrorBook "
                "(user_id, word_id, error_type, error_count, resolved, last_error_at) "
                "VALUES (?, ?, ?, 1, 0, ?)",
                (user_id, word_id, error_type, _now()),
            )
        self.conn.commit()

    def mark_resolved(self, user_id: int, word_id: int) -> None:
        self.conn.execute(
            "UPDATE ErrorBook SET resolved = 1 WHERE user_id = ? AND word_id = ?",
            (user_id, word_id),
        )
        self.conn.commit()

    def list_errors(self, user_id: int, include_resolved: bool = False) -> List[sqlite3.Row]:
        sql = (
            "SELECT e.*, w.spelling, w.meaning_cn, w.phonetic, w.pos, w.grade "
            "FROM ErrorBook e JOIN Word w ON e.word_id = w.id WHERE e.user_id = ?"
        )
        if not include_resolved:
            sql += " AND e.resolved = 0"
        sql += " ORDER BY e.error_count DESC, e.last_error_at DESC"
        return self.conn.execute(sql, (user_id,)).fetchall()

    def count(self, user_id: int, include_resolved: bool = False) -> int:
        sql = "SELECT COUNT(*) AS c FROM ErrorBook WHERE user_id = ?"
        if not include_resolved:
            sql += " AND resolved = 0"
        return self.conn.execute(sql, (user_id,)).fetchone()["c"]


class ReviewScheduleDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get(self, user_id: int, word_id: int) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM ReviewSchedule WHERE user_id = ? AND word_id = ?",
            (user_id, word_id),
        ).fetchone()

    def ensure(self, user_id: int, word_id: int, now: Optional[str] = None) -> sqlite3.Row:
        row = self.get(user_id, word_id)
        if row:
            return row
        self.conn.execute(
            "INSERT INTO ReviewSchedule "
            "(user_id, word_id, repetition, easiness_factor, interval_days, "
            "next_review_at, last_review_at, status) "
            "VALUES (?, ?, 0, 2.5, 0, ?, '', 'new')",
            (user_id, word_id, now or _now()),
        )
        self.conn.commit()
        return self.get(user_id, word_id)

    def update(self, user_id: int, word_id: int, repetition: int,
               easiness_factor: float, interval_days: int,
               next_review_at: str, status: str) -> None:
        self.conn.execute(
            "UPDATE ReviewSchedule SET repetition = ?, easiness_factor = ?, "
            "interval_days = ?, next_review_at = ?, last_review_at = ?, status = ? "
            "WHERE user_id = ? AND word_id = ?",
            (repetition, easiness_factor, interval_days, next_review_at,
             _now(), status, user_id, word_id),
        )
        self.conn.commit()

    def due(self, user_id: int, now: Optional[str] = None, limit: int = 20) -> List[sqlite3.Row]:
        """返回到期需复习的单词（含 Word 信息），薄弱优先。"""
        now = now or _now()
        return self.conn.execute(
            "SELECT r.*, w.spelling, w.meaning_cn, w.phonetic, w.pos, w.grade, w.id AS word_id "
            "FROM ReviewSchedule r JOIN Word w ON r.word_id = w.id "
            "WHERE r.user_id = ? AND r.next_review_at <= ? "
            "ORDER BY r.easiness_factor ASC, r.next_review_at ASC LIMIT ?",
            (user_id, now, limit),
        ).fetchall()

    def count_due(self, user_id: int, now: Optional[str] = None) -> int:
        now = now or _now()
        return self.conn.execute(
            "SELECT COUNT(*) AS c FROM ReviewSchedule WHERE user_id = ? AND next_review_at <= ?",
            (user_id, now),
        ).fetchone()["c"]