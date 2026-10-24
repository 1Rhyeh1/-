"""学习 Tab：选择年级与测试模式，持续推送单词进行学习。"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.ui.quiz_widget import QuizWidget


class StudyTab(QWidget):
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
        bar.addWidget(QLabel("年级："))
        self.grade_combo = QComboBox()
        self.grade_combo.addItems(["全部", "初中", "高中"])
        bar.addWidget(self.grade_combo)

        bar.addSpacing(16)
        bar.addWidget(QLabel("模式："))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("拼写测试", "spell")
        self.mode_combo.addItem("词义选择", "meaning")
        bar.addWidget(self.mode_combo)

        bar.addStretch(1)
        root.addLayout(bar)

        self.quiz = QuizWidget(self.service, self.user_id)
        self.quiz.provider = self._provide_word
        self.quiz.answered.connect(lambda _res: self.progress.emit())
        root.addWidget(self.quiz, 1)

        self.grade_combo.currentIndexChanged.connect(self._restart)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)

        self._restart()

    def _current_grade(self):
        text = self.grade_combo.currentText()
        return None if text == "全部" else text

    def _provide_word(self):
        return self.service.pick_study_word(self.user_id, self._current_grade())

    def _on_mode_changed(self) -> None:
        self.quiz.set_mode(self.mode_combo.currentData())

    def _restart(self) -> None:
        self.quiz.set_mode(self.mode_combo.currentData())
        word = self._provide_word()
        self.quiz.start([word] if word is not None else [])

    def refresh(self) -> None:
        self._restart()