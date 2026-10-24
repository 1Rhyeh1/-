"""全局配置：路径、常量。"""
import os
import sys


def _app_dir() -> str:
    """返回应用根目录，兼容 PyInstaller 打包后的运行环境。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


APP_DIR = _app_dir()
DATA_DIR = os.path.join(APP_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "words.db")
os.makedirs(DATA_DIR, exist_ok=True)

# 记忆算法参数
DEFAULT_EASINESS_FACTOR = 2.5
MIN_EASINESS_FACTOR = 1.3
MAX_SPELLING_DISTANCE = 2  # 编辑距离 <= 2 判定为拼写失误

# 启动时优先推送的薄弱词汇数量
DAILY_REVIEW_LIMIT = 20