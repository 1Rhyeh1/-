"""学习服务闭环集成测试：作答 -> 分析 -> 错词本 -> 复习计划。"""
import sqlite3
import unittest

from app.db.database import init_db
from app.db.models import WordDAO, UserDAO
from app.core.service import LearningService


class TestLearningService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        init_db(self.conn)
        self.service = LearningService(self.conn)
        self.user_id = self.service.users.get_or_create("tester", "初中")
        w = WordDAO(self.conn)
        self.apple_id = w.add("apple", "苹果", grade="初中")
        self.effect_id = w.add("effect", "效果", grade="高中",
                               confusion_group="CF_AFFECT")
        self.affect_id = w.add("affect", "影响", grade="高中",
                               confusion_group="CF_AFFECT")

    def test_correct_answer_no_error_book(self):
        res = self.service.submit_answer(self.user_id, self.apple_id, "spell", "apple")
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["error_type"], "none")
        self.assertEqual(res["interval_days"], 1)
        self.assertEqual(self.service.error_book.count(self.user_id), 0)

    def test_wrong_answer_creates_error_and_reschedule(self):
        res = self.service.submit_answer(self.user_id, self.apple_id, "spell", "aple")
        self.assertFalse(res["is_correct"])
        self.assertEqual(res["error_type"], "spelling")
        self.assertEqual(self.service.error_book.count(self.user_id), 1)
        # 答错后间隔回到 1 天
        self.assertEqual(res["interval_days"], 1)

    def test_confusion_detected(self):
        res = self.service.submit_answer(self.user_id, self.affect_id, "spell", "effect")
        self.assertFalse(res["is_correct"])
        self.assertEqual(res["error_type"], "confusion")

    def test_meaning_error(self):
        res = self.service.submit_answer(self.user_id, self.apple_id, "meaning", "香蕉")
        self.assertFalse(res["is_correct"])
        self.assertEqual(res["error_type"], "meaning")

    def test_resolve_after_correct(self):
        self.service.submit_answer(self.user_id, self.apple_id, "spell", "aple")
        self.assertEqual(self.service.error_book.count(self.user_id), 1)
        self.service.submit_answer(self.user_id, self.apple_id, "spell", "apple")
        self.assertEqual(self.service.error_book.count(self.user_id), 0)

    def test_due_words_returns_scheduled(self):
        self.service.submit_answer(self.user_id, self.apple_id, "spell", "apple")
        # 刚答对，下次复习在 1 天后，不应立即到期
        self.assertEqual(len(self.service.due_words(self.user_id)), 0)
        self.assertEqual(self.service.reviews.count_due(self.user_id), 0)

    def test_stats_and_chart(self):
        self.service.submit_answer(self.user_id, self.apple_id, "spell", "aple")
        self.service.submit_answer(self.user_id, self.effect_id, "spell", "efect")
        self.service.submit_answer(self.user_id, self.apple_id, "meaning", "香蕉")
        stats = self.service.stats(self.user_id)
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["correct"], 0)
        chart = self.service.error_type_chart(self.user_id)
        self.assertEqual(chart["拼写失误"], 2)
        self.assertEqual(chart["词义错误"], 1)

    def test_weak_word_ranking(self):
        for _ in range(3):
            self.service.submit_answer(self.user_id, self.apple_id, "spell", "aple")
        ranking = self.service.weak_word_ranking(self.user_id)
        self.assertEqual(ranking[0]["spelling"], "apple")
        self.assertEqual(ranking[0]["error_count"], 3)


if __name__ == "__main__":
    unittest.main()