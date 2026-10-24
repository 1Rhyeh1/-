"""相似度与编辑距离单元测试。"""
import unittest

from app.core.similarity import (
    edit_distance,
    find_most_similar,
    is_close_spelling,
    normalize,
    similarity_ratio,
)


class TestSimilarity(unittest.TestCase):
    def test_edit_distance_basic(self):
        self.assertEqual(edit_distance("apple", "apple"), 0)
        self.assertEqual(edit_distance("apple", "aple"), 1)
        self.assertEqual(edit_distance("apple", "appel"), 2)
        self.assertEqual(edit_distance("", "abc"), 3)
        self.assertEqual(edit_distance("abc", ""), 3)

    def test_normalize(self):
        self.assertEqual(normalize("  Apple  "), "apple")
        self.assertEqual(normalize(None), "")

    def test_is_close_spelling(self):
        self.assertTrue(is_close_spelling("apple", "aple", 2))
        self.assertFalse(is_close_spelling("apple", "banana", 2))
        self.assertTrue(is_close_spelling("BOOK", "book", 2))

    def test_similarity_ratio_bounds(self):
        self.assertAlmostEqual(similarity_ratio("apple", "apple"), 1.0)
        self.assertLess(similarity_ratio("apple", "axxxx"), 0.5)

    def test_find_most_similar(self):
        word, dist = find_most_similar("aple", ["apple", "banana", "apply"])
        self.assertEqual(word, "apple")
        self.assertEqual(dist, 1)
        self.assertEqual(find_most_similar("x", []), (None, None))


if __name__ == "__main__":
    unittest.main()