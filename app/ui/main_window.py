"""主窗口：应用头部状态栏 + 学习 / 复习 / 错词本 三个 Tab。"""
import os

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.service import LearningService
from app.ui.error_book_tab import ErrorBookTab
from app.ui.review_tab import ReviewTab
from app.ui.study_tab import StudyTab


def load_stylesheet() -> str:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles.qss")
    try:
        with open(path, "r", encoding="utf-8") as fp:
            return fp.read()
    except OSError:
        return ""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("中学生英语单词智能记忆与错词分析系统")
        self.resize(1100, 760)

        self.service = LearningService()
        self.user_id = self.service.users.get_or_create("默认学生", "初中")

        self._build_ui()
        self.setStyleSheet(load_stylesheet())
        self.refresh_header()

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("RootWidget")
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("Header")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 14, 24, 14)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("单词智能记忆系统")
        title.setObjectName("HeaderTitle")
        sub = QLabel("间隔重复 · NLP 错词分析 · 完全离线运行")
        sub.setObjectName("HeaderSub")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        hl.addLayout(title_box)
        hl.addStretch(1)

        self.stats_label = QLabel("")
        self.stats_label.setObjectName("HeaderSub")
        hl.addWidget(self.stats_label)
        layout.addWidget(header)

        self.tabs = QTabWidget()
        self.study_tab = StudyTab(self.service, self.user_id)
        self.review_tab = ReviewTab(self.service, self.user_id)
        self.error_tab = ErrorBookTab(self.service, self.user_id)

        self.tabs.addTab(self.study_tab, "学习")
        self.tabs.addTab(self.review_tab, "复习")
        self.tabs.addTab(self.error_tab, "错词本")
        layout.addWidget(self.tabs, 1)

        self.study_tab.progress.connect(self.refresh_header)
        self.review_tab.progress.connect(self.refresh_header)
        self.error_tab.progress.connect(self.refresh_header)
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index: int) -> None:
        widget = self.tabs.widget(index)
        if hasattr(widget, "refresh"):
            widget.refresh()
        self.refresh_header()

    def refresh_header(self) -> None:
        stats = self.service.stats(self.user_id)
        due = self.service.reviews.count_due(self.user_id)
        errors = self.service.error_book.count(self.user_id)
        self.stats_label.setText(
            "正确率 {0:.0f}%　·　到期复习 {1}　·　待攻克错词 {2}".format(
                stats["accuracy"] * 100, due, errors
            )
        )