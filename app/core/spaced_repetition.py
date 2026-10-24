"""动态间隔重复调度：SM-2（SuperMemo-2）算法实现。

SM-2 维护三个关键参数：
- repetition      ：连续答对次数 n
- easiness_factor ：难度因子 EF（默认 2.5，下限 1.3）
- interval_days   ：当前复习间隔（天）

答对（quality >= 3）时按 1 天、6 天、interval*EF 递推；
答错（quality < 3）时重置 repetition 并将间隔退回 1 天。
"""
from datetime import datetime, timedelta
from typing import Dict, Optional

from app.config import DEFAULT_EASINESS_FACTOR, MIN_EASINESS_FACTOR
from app.core.error_analyzer import ERROR_SPELLING, ERROR_CONFUSION


def quality_from_result(is_correct: bool, error_type: str = "none",
                        prior_errors: int = 0) -> int:
    """将作答结果映射为 SM-2 的 quality（0-5）。

    - 答对：5；若历史上已有错误则记 4（说明仍需巩固）
    - 答错且为形近词混淆 / 拼写失误：2（接近掌握）
    - 答错且为词义错误或其它：1
    """
    if is_correct:
        return 4 if prior_errors > 0 else 5
    if error_type in (ERROR_SPELLING, ERROR_CONFUSION):
        return 2
    return 1


def sm2_update(quality: int, repetition: int, easiness_factor: float,
               interval_days: int) -> Dict[str, float]:
    """执行一次 SM-2 更新，返回新的 repetition / EF / interval。"""
    quality = max(0, min(5, int(quality)))

    if quality < 3:
        repetition = 0
        interval_days = 1
    else:
        repetition += 1
        if repetition == 1:
            interval_days = 1
        elif repetition == 2:
            interval_days = 6
        else:
            interval_days = round(interval_days * easiness_factor)

    ef = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ef < MIN_EASINESS_FACTOR:
        ef = MIN_EASINESS_FACTOR

    return {
        "repetition": repetition,
        "easiness_factor": round(ef, 4),
        "interval_days": int(interval_days),
    }


def _status_from_repetition(repetition: int) -> str:
    if repetition == 0:
        return "learning"
    if repetition < 3:
        return "learning"
    return "review"


def schedule_next(quality: int, repetition: int = 0,
                  easiness_factor: float = DEFAULT_EASINESS_FACTOR,
                  interval_days: int = 0,
                  now: Optional[datetime] = None) -> Dict[str, object]:
    """计算下一次复习安排。返回可直接写入数据库的字段字典。"""
    now = now or datetime.now()
    updated = sm2_update(quality, repetition, easiness_factor, interval_days)
    next_review = now + timedelta(days=updated["interval_days"])
    return {
        "repetition": updated["repetition"],
        "easiness_factor": updated["easiness_factor"],
        "interval_days": updated["interval_days"],
        "next_review_at": next_review.isoformat(timespec="seconds"),
        "status": _status_from_repetition(updated["repetition"]),
    }