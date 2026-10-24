"""SM-2 间隔重复算法单元测试。"""
import unittest
from datetime import datetime

from app.core.spaced_repetition import (
    DEFAULT_EASINESS_FACTOR,
    quality_from_result,
    schedule_next,
    sm2_update,
)


class TestSpacedRepetition(unittest.TestCase):
    def test_first_correct(self):
        r = sm2_update(5, 0, DEFAULT_EASINESS_FACTOR, 0)
        self.assertEqual(r["repetition"], 1)
        self.assertEqual(r["interval_days"], 1)
        self.assertGreater(r["easiness_factor"], DEFAULT_EASINESS_FACTOR)

    def test_second_correct_interval_six(self):
        r = sm2_update(5, 1, 2.6, 1)
        self.assertEqual(r["repetition"], 2)
        self.assertEqual(r["interval_days"], 6)

    def test_third_correct_uses_ef(self):
        r = sm2_update(5, 2, 2.6, 6)
        self.assertEqual(r["repetition"], 3)
        self.assertEqual(r["interval_days"], round(6 * 2.6))

    def test_wrong_resets(self):
        r = sm2_update(1, 5, 2.6, 30)
        self.assertEqual(r["repetition"], 0)
        self.assertEqual(r["interval_days"], 1)
        self.assertLess(r["easiness_factor"], 2.6)

    def test_ef_floor(self):
        ef = 1.3
        for _ in range(10):
            r = sm2_update(0, 0, ef, 1)
            ef = r["easiness_factor"]
        self.assertGreaterEqual(r["easiness_factor"], 1.3)

    def test_schedule_next_sets_next_review(self):
        now = datetime(2026, 1, 1, 8, 0, 0)
        plan = schedule_next(5, 0, DEFAULT_EASINESS_FACTOR, 0, now=now)
        self.assertEqual(plan["interval_days"], 1)
        self.assertTrue(plan["next_review_at"].startswith("2026-01-02"))
        self.assertEqual(plan["status"], "learning")

    def test_status_review_after_three(self):
        now = datetime(2026, 1, 1)
        plan = schedule_next(5, 2, 2.6, 6, now=now)
        self.assertEqual(plan["status"], "review")

    def test_quality_mapping(self):
        self.assertEqual(quality_from_result(True), 5)
        self.assertEqual(quality_from_result(True, prior_errors=2), 4)
        self.assertEqual(quality_from_result(False, "spelling"), 2)
        self.assertEqual(quality_from_result(False, "meaning"), 1)


if __name__ == "__main__":
    unittest.main()