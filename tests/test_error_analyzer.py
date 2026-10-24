"""错词分析模块单元测试（核心）。"""
import unittest

from app.core.error_analyzer import (
    ERROR_CONFUSION,
    ERROR_MEANING,
    ERROR_NONE,
    ERROR_SPELLING,
    analyze_answer,
    analyze_spelling,
)


class TestErrorAnalyzer(unittest.TestCase):
    def test_correct_spelling(self):
        etype, dist = analyze_spelling("apple", "apple", ["apply"])
        self.assertEqual(etype, ERROR_NONE)
        self.assertEqual(dist, 0)
        # 大小写/空白不影响判定
        self.assertEqual(analyze_spelling("  Apple ", "apple")[0], ERROR_NONE)

    def test_spelling_mistake_within_threshold(self):
        etype, dist = analyze_spelling("aple", "apple", [])
        self.assertEqual(etype, ERROR_SPELLING)
        self.assertEqual(dist, 1)

    def test_empty_answer_is_spelling_error(self):
        etype, dist = analyze_spelling("", "apple", [])
        self.assertEqual(etype, ERROR_SPELLING)
        self.assertEqual(dist, 5)

    def test_confusion_exact_other_word(self):
        # affect 的形近词为 effect，学生拼成了 effect -> 混淆
        etype, _ = analyze_spelling("effect", "affect", ["effect"])
        self.assertEqual(etype, ERROR_CONFUSION)

    def test_confusion_closer_to_other_word(self):
        # 学生写成 "adpt"，"adapt" 与 "adopt" 都在形近词组里
        etype, _ = analyze_spelling("adopt", "adapt", ["adopt"])
        self.assertEqual(etype, ERROR_CONFUSION)

    def test_typo_stays_spelling_not_confusion(self):
        # "affct" 距离 affect=1，距离 effect=2，应判为拼写失误
        etype, dist = analyze_spelling("affct", "affect", ["effect"])
        self.assertEqual(etype, ERROR_SPELLING)
        self.assertEqual(dist, 1)

    def test_meaning_wrong(self):
        ok, etype, dist = analyze_answer(
            "meaning", "香蕉", correct_meaning="苹果"
        )
        self.assertFalse(ok)
        self.assertEqual(etype, ERROR_MEANING)
        self.assertEqual(dist, 0)

    def test_meaning_correct(self):
        ok, etype, _ = analyze_answer("meaning", "苹果", correct_meaning="苹果")
        self.assertTrue(ok)
        self.assertEqual(etype, ERROR_NONE)

    def test_analyze_answer_spelling_path(self):
        ok, etype, dist = analyze_answer(
            "spell", "efect", correct_spelling="effect", confusion_words=["affect"]
        )
        self.assertFalse(ok)
        self.assertEqual(etype, ERROR_SPELLING)
        self.assertEqual(dist, 1)


if __name__ == "__main__":
    unittest.main()