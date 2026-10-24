"""NLP 错词分析模块（核心）。

在离线条件下，基于「编辑距离 + 本地形近词表」将学生的错误划分为三类：
- spelling  ：拼写失误（编辑距离较小，如距离 <= 2）
- confusion ：形近词混淆（与同形近词组的其它词一致或更接近）
- meaning   ：词义错误（词义选择题答错）
- none      ：回答正确
"""
from typing import List, Optional, Sequence, Tuple

from app.config import MAX_SPELLING_DISTANCE
from app.core.similarity import edit_distance, normalize

ERROR_NONE = "none"
ERROR_SPELLING = "spelling"
ERROR_CONFUSION = "confusion"
ERROR_MEANING = "meaning"

ERROR_LABELS = {
    ERROR_NONE: "正确",
    ERROR_SPELLING: "拼写失误",
    ERROR_CONFUSION: "形近词混淆",
    ERROR_MEANING: "词义错误",
}


def analyze_spelling(
    user_answer: str,
    correct_spelling: str,
    confusion_words: Optional[Sequence[str]] = None,
    max_distance: int = MAX_SPELLING_DISTANCE,
) -> Tuple[str, int]:
    """分析拼写类作答，返回 (error_type, edit_distance)。"""
    ua = normalize(user_answer)
    cw = normalize(correct_spelling)
    confusion = [normalize(w) for w in (confusion_words or [])]

    if ua == cw:
        return ERROR_NONE, 0
    if ua == "":
        return ERROR_SPELLING, len(cw)

    dist = edit_distance(ua, cw)

    # 与形近词组完全一致 -> 混淆
    if ua in confusion:
        return ERROR_CONFUSION, dist

    # 与某个形近词更接近，且达到判定阈值 -> 混淆
    for candidate in confusion:
        cand_dist = edit_distance(ua, candidate)
        if cand_dist <= max_distance and cand_dist < dist:
            return ERROR_CONFUSION, dist

    # 否则视为拼写失误（距离越小越可能是手误）
    return ERROR_SPELLING, dist


def analyze_answer(
    test_type: str,
    user_answer: str,
    correct_spelling: str = "",
    correct_meaning: str = "",
    confusion_words: Optional[Sequence[str]] = None,
    max_distance: int = MAX_SPELLING_DISTANCE,
) -> Tuple[bool, str, int]:
    """统一入口。返回 (is_correct, error_type, edit_distance)。"""
    if test_type == "meaning":
        if normalize(user_answer) == normalize(correct_meaning):
            return True, ERROR_NONE, 0
        return False, ERROR_MEANING, 0

    error_type, dist = analyze_spelling(
        user_answer, correct_spelling, confusion_words, max_distance
    )
    return error_type == ERROR_NONE, error_type, dist


def label_for(error_type: str) -> str:
    return ERROR_LABELS.get(error_type, error_type)