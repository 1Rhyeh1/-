"""学习服务：串联「作答 -> 错词分析 -> 记录 -> 错词本 -> 复习计划」闭环。"""
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.error_analyzer import label_for, analyze_answer
from app.core.spaced_repetition import (
    quality_from_result,
    schedule_next,
    DEFAULT_EASINESS_FACTOR,
)
from app.db.database import get_connection
from app.db.models import (
    ErrorBookDAO,
    ReviewScheduleDAO,
    TestRecordDAO,
    UserDAO,
    WordDAO,
)


class LearningService:
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self.conn = conn or get_connection()
        self.users = UserDAO(self.conn)
        self.words = WordDAO(self.conn)
        self.records = TestRecordDAO(self.conn)
        self.error_book = ErrorBookDAO(self.conn)
        self.reviews = ReviewScheduleDAO(self.conn)

    @staticmethod
    def word_id_of(row) -> int:
        """统一从各类查询结果中取出 Word 主键。"""
        keys = row.keys()
        if "word_id" in keys and row["word_id"] is not None:
            return row["word_id"]
        return row["id"]

    # ---------- 查询 ----------
    def pick_study_word(self, user_id: int, grade: Optional[str] = None) -> Optional[sqlite3.Row]:
        """选择下一个学习单词：优先到期复习词，其次未学过的词。"""
        due = self.reviews.due(user_id, limit=1)
        if due:
            return self.words.get(due[0]["word_id"])
        rows = self.words.all(grade)
        for row in rows:
            if self.reviews.get(user_id, row["id"]) is None:
                return row
        return rows[0] if rows else None

    def due_words(self, user_id: int, limit: int = 20) -> List[sqlite3.Row]:
        return self.reviews.due(user_id, limit=limit)

    def error_list(self, user_id: int, include_resolved: bool = False) -> List[sqlite3.Row]:
        return self.error_book.list_errors(user_id, include_resolved)

    def stats(self, user_id: int) -> Dict[str, Any]:
        return self.records.stats(user_id)

    # ---------- 核心：提交作答 ----------
    def submit_answer(self, user_id: int, word_id: int, test_type: str,
                      user_answer: str) -> Dict[str, Any]:
        word = self.words.get(word_id)
        if word is None:
            raise ValueError(f"word_id {word_id} 不存在")

        confusion = self.words.confusion_words(word_id)
        is_correct, error_type, dist = analyze_answer(
            test_type=test_type,
            user_answer=user_answer,
            correct_spelling=word["spelling"],
            correct_meaning=word["meaning_cn"],
            confusion_words=confusion,
        )

        # 1) 记录测试结果
        self.records.add(user_id, word_id, test_type, user_answer,
                         is_correct, error_type, dist)

        # 2) 错词本维护
        prior_errors = self._error_count(user_id, word_id)
        if is_correct:
            self.error_book.mark_resolved(user_id, word_id)
        else:
            self.error_book.upsert_error(user_id, word_id, error_type)

        # 3) 间隔重复调度
        current = self.reviews.ensure(user_id, word_id)
        quality = quality_from_result(is_correct, error_type, prior_errors)
        plan = schedule_next(
            quality=quality,
            repetition=current["repetition"],
            easiness_factor=current["easiness_factor"] or DEFAULT_EASINESS_FACTOR,
            interval_days=current["interval_days"],
        )
        self.reviews.update(
            user_id, word_id,
            plan["repetition"], plan["easiness_factor"],
            plan["interval_days"], plan["next_review_at"], plan["status"],
        )

        return {
            "is_correct": is_correct,
            "error_type": error_type,
            "error_label": label_for(error_type),
            "edit_distance": dist,
            "quality": quality,
            "next_review_at": plan["next_review_at"],
            "interval_days": plan["interval_days"],
            "status": plan["status"],
            "correct_spelling": word["spelling"],
            "correct_meaning": word["meaning_cn"],
        }

    def _error_count(self, user_id: int, word_id: int) -> int:
        row = self.conn.execute(
            "SELECT error_count FROM ErrorBook WHERE user_id = ? AND word_id = ?",
            (user_id, word_id),
        ).fetchone()
        return row["error_count"] if row else 0

    # ---------- 图表数据 ----------
    def error_type_chart(self, user_id: int) -> Dict[str, int]:
        dist = self.records.error_type_distribution(user_id)
        return {
            "拼写失误": dist.get("spelling", 0),
            "形近词混淆": dist.get("confusion", 0),
            "词义错误": dist.get("meaning", 0),
        }

    def weak_word_ranking(self, user_id: int, top: int = 10) -> List[Dict[str, Any]]:
        rows = self.error_book.list_errors(user_id, include_resolved=True)
        return [
            {"spelling": r["spelling"], "error_count": r["error_count"],
             "error_type": r["error_type"]}
            for r in rows[:top]
        ]

    def now_iso(self) -> str:
        return datetime.now().isoformat(timespec="seconds")