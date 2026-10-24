"""matplotlib 图表组件，用于嵌入错词本可视化。"""
from typing import Dict, List

import matplotlib

matplotlib.use("QtAgg")
matplotlib.rcParams["font.sans-serif"] = [
    "Microsoft YaHei", "SimHei", "PingFang SC", "DejaVu Sans"
]
matplotlib.rcParams["axes.unicode_minus"] = False

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

_PRIMARY = "#4a6cf7"
_WARM = "#ff8a65"
_GREEN = "#26c6a4"


class ChartWidget(QWidget):
    """包含两张图（错误类型分布 + 薄弱词排行）的图表容器。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.figure = Figure(figsize=(5, 5.2), dpi=100)
        self.figure.patch.set_facecolor("#ffffff")
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self._ax_pie = self.figure.add_subplot(2, 1, 1)
        self._ax_bar = self.figure.add_subplot(2, 1, 2)
        self.figure.subplots_adjust(hspace=0.55, left=0.28, right=0.96,
                                    top=0.9, bottom=0.14)
        self.render({}, [])

    def render(self, error_types: Dict[str, int], weak_words: List[Dict]) -> None:
        self._render_pie(error_types)
        self._render_bar(weak_words)
        self.canvas.draw_idle()

    def _render_pie(self, error_types: Dict[str, int]) -> None:
        ax = self._ax_pie
        ax.clear()
        ax.set_title("错误类型分布", fontsize=11, color="#22335c")
        data = {k: v for k, v in error_types.items() if v > 0}
        if not data:
            ax.text(0.5, 0.5, "暂无错题数据", ha="center", va="center",
                    transform=ax.transAxes, color="#9aa7bd")
            ax.axis("off")
            return
        colors = [_PRIMARY, _WARM, _GREEN, "#b39ddb"]
        ax.pie(list(data.values()), labels=list(data.keys()),
               autopct="%1.0f%%", colors=colors[:len(data)],
               textprops={"fontsize": 9})
        ax.axis("equal")

    def _render_bar(self, weak_words: List[Dict]) -> None:
        ax = self._ax_bar
        ax.clear()
        ax.set_title("薄弱词汇 Top", fontsize=11, color="#22335c")
        if not weak_words:
            ax.text(0.5, 0.5, "暂无错题数据", ha="center", va="center",
                    transform=ax.transAxes, color="#9aa7bd")
            ax.axis("off")
            return
        items = weak_words[:8][::-1]
        names = [it["spelling"] for it in items]
        counts = [it["error_count"] for it in items]
        ax.barh(names, counts, color=_PRIMARY)
        ax.tick_params(labelsize=9)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.set_xlabel("错误次数", fontsize=9)