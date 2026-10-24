"""字符串相似度工具：编辑距离、形近词判定。

优先使用 rapidfuzz（纯 C 实现、离线、速度快）；若环境未安装则退化为
纯 Python 动态规划实现，保证离线可运行。
"""
from typing import List

try:  # pragma: no cover - 取决于环境是否安装 rapidfuzz
    from rapidfuzz.distance import Levenshtein as _RF_Levenshtein

    def edit_distance(a: str, b: str) -> int:
        return _RF_Levenshtein.distance(a, b)

    def similarity_ratio(a: str, b: str) -> float:
        """归一化相似度，范围 [0, 1]。"""
        return _RF_Levenshtein.normalized_similarity(a, b)

    _BACKEND = "rapidfuzz"
except ImportError:  # pragma: no cover
    def edit_distance(a: str, b: str) -> int:
        if a == b:
            return 0
        if not a:
            return len(b)
        if not b:
            return len(a)
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            cur = [i]
            for j, cb in enumerate(b, 1):
                cost = 0 if ca == cb else 1
                cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
            prev = cur
        return prev[-1]

    def similarity_ratio(a: str, b: str) -> float:
        if not a and not b:
            return 1.0
        denom = max(len(a), len(b))
        return 1.0 if denom == 0 else 1.0 - edit_distance(a, b) / denom

    _BACKEND = "python"


def normalize(text: str) -> str:
    """统一小写并去除首尾空白，用于比对。"""
    return (text or "").strip().lower()


def is_close_spelling(a: str, b: str, max_distance: int = 2) -> bool:
    return edit_distance(normalize(a), normalize(b)) <= max_distance


def find_most_similar(word: str, candidates: List[str]):
    """返回 (最相似单词, 距离)，候选为空时返回 (None, None)。"""
    word = normalize(word)
    best_word, best_dist = None, None
    for candidate in candidates:
        dist = edit_distance(word, normalize(candidate))
        if best_dist is None or dist < best_dist:
            best_word, best_dist = candidate, dist
    return best_word, best_dist


def backend_name() -> str:
    return _BACKEND