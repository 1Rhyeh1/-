"""复习 Tab：智能推送到期（薄弱优先）词汇进行复习。"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.config import DAILY_REVIEW_LIMIT
from app.ui.quiz_widget import QuizWidget


class ReviewTab(QWidget):
    progress = Signal()

    def __init__(self, service, user_id: int, parent=None):
        super().__init__(parent)
        self.service = service
        self.user_id = user_id
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        bar = QHBoxLayout()
        self.info = QLabel("到期复习：0 个")
        self.info.setObjectName("HeaderSub")
        bar.addWidget(self.info)
        bar.addStretch(1)
        self.refresh_btn = QPushButton("重新加载")
        self.refresh_btn.setObjectName("Secondary")
        self.refresh_btn.clicked.connect(self.refresh)
        bar.addWidget(self.refresh_btn)
        root.addLayout(bar)

        self.quiz = QuizWidget(self.service, self.user_id)
        self.quiz.answered.connect(lambda _res: self.progress.emit())
        root.addWidget(self.quiz, 1)

        self.refresh()

    def refresh(self) -> None:
        due = self.service.due_words(self.user_id, limit=DAILY_REVIEW_LIMIT)
        total_due = self.service.reviews.count_due(self.user_id)
        self.info.setText("到期复习：{0} 个（本次加载 {1} 个）".format(total_due, len(due)))
        self.quiz.set_mode("spell")
        if due:
            self.quiz.start(due)
        else:
            self.quiz.clear()
            self.quiz.prompt_word.setText("太棒了！当前没有到期需复习的单词")