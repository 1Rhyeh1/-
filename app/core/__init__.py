"""核心算法层：相似度、错词分析、间隔重复、学习服务。"""
from app.core import error_analyzer, similarity, spaced_repetition
from app.core.service import LearningService

__all__ = [
    "error_analyzer",
    "similarity",
    "spaced_repetition",
    "LearningService",
]