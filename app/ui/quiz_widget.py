"""通用测验组件：支持拼写测试与词义选择，供学习 / 复习 / 错词强化复用。"""
from typing import Callable, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class QuizWidget(QWidget):
    answered = Signal(dict)

    def __init__(self, service, user_id: int, parent=None):
        super().__init__(parent)
        self.service = service
        self.user_id = user_id
        self.mode = "spell"
        self.queue: List = []
        self.current = None
        self.answered_flag = False
        self.provider: Optional[Callable[[], Optional[object]]] = None
        self.option_buttons: List[QRadioButton] = []
        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(16)

        self.prompt_type = QLabel("请写出对应英文单词")
        self.prompt_type.setObjectName("Phonetic")
        self.prompt_type.setAlignment(Qt.AlignCenter)

        self.prompt_word = QLabel("—")
        self.prompt_word.setObjectName("PromptMeaning")
        self.prompt_word.setAlignment(Qt.AlignCenter)
        self.prompt_word.setWordWrap(True)

        self.prompt_phonetic = QLabel("")
        self.prompt_phonetic.setObjectName("Phonetic")
        self.prompt_phonetic.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(self.prompt_type)
        card_layout.addWidget(self.prompt_word)
        card_layout.addWidget(self.prompt_phonetic)

        self.input = QLineEdit()
        self.input.setPlaceholderText("输入英文拼写后按回车提交…")
        self.input.setAlignment(Qt.AlignCenter)
        self.input.returnPressed.connect(self._submit_spelling)
        card_layout.addWidget(self.input)

        self.options_box = QWidget()
        self.options_layout = QVBoxLayout(self.options_box)
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.options_layout.setSpacing(8)
        card_layout.addWidget(self.options_box)
        self.options_box.hide()

        self.feedback = QLabel("")
        self.feedback.setWordWrap(True)
        self.feedback.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.feedback)

        root.addWidget(card)

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.submit_btn = QPushButton("提交")
        self.submit_btn.clicked.connect(self._on_submit)
        self.next_btn = QPushButton("下一题")
        self.next_btn.setObjectName("Secondary")
        self.next_btn.clicked.connect(self._next)
        self.next_btn.setEnabled(False)
        btns.addWidget(self.submit_btn)
        btns.addWidget(self.next_btn)
        root.addLayout(btns)
        root.addStretch(1)

    # ---------- 对外接口 ----------
    def set_mode(self, mode: str) -> None:
        self.mode = mode
        if self.current is not None and not self.answered_flag:
            self._render_question()

    def start(self, words: List) -> None:
        self.queue = list(words)
        self._next()

    def clear(self) -> None:
        self.queue = []
        self.current = None
        self.answered_flag = False
        self.feedback.setText("")
        self.submit_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.prompt_type.setText("")
        self.prompt_word.setText("暂无待学习单词")
        self.prompt_phonetic.setText("")
        self.input.hide()
        self.options_box.hide()

    # ---------- 流程 ----------
    def _next(self) -> None:
        self.answered_flag = False
        self.feedback.setText("")
        self.prompt_word.setObjectName("PromptMeaning")
        self._repolish(self.prompt_word)
        self.submit_btn.setEnabled(True)
        self.next_btn.setEnabled(False)

        if not self.queue and self.provider is not None:
            word = self.provider()
            if word is not None:
                self.queue.append(word)

        if not self.queue:
            self.clear()
            return

        self.current = self.queue.pop(0)
        self._render_question()

    def _render_question(self) -> None:
        w = self.current
        self.input.clear()
        for btn in self.option_buttons:
            btn.setChecked(False)
        if self.mode == "spell":
            self.prompt_type.setText("请写出对应英文单词")
            self.prompt_word.setObjectName("PromptMeaning")
            self.prompt_word.setText(w["meaning_cn"])
            self.prompt_phonetic.setText(w["phonetic"] or "")
            self.input.show()
            self.options_box.hide()
            self.input.setFocus()
        else:
            self.prompt_type.setText("请选择正确的中文词义")
            self.prompt_word.setObjectName("PromptWord")
            self.prompt_word.setText(w["spelling"])
            self.prompt_phonetic.setText(w["phonetic"] or "")
            self.input.hide()
            self.options_box.show()
            self._build_options(w)
        self._repolish(self.prompt_word)

    def _build_options(self, word) -> None:
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.option_buttons = []

        correct = word["meaning_cn"]
        pool = [r["meaning_cn"] for r in self.service.words.all()
                if r["meaning_cn"] != correct]
        import random
        random.shuffle(pool)
        options = pool[:3] + [correct]
        random.shuffle(options)
        for opt in options:
            btn = QRadioButton(opt)
            self.options_layout.addWidget(btn)
            self.option_buttons.append(btn)

    # ---------- 提交 ----------
    def _on_submit(self) -> None:
        if self.answered_flag or self.current is None:
            return
        if self.mode == "spell":
            self._submit_spelling()
        else:
            self._submit_meaning()

    def _submit_spelling(self) -> None:
        if self.answered_flag or self.current is None:
            return
        self._grade(self.input.text())

    def _submit_meaning(self) -> None:
        if self.answered_flag or self.current is None:
            return
        answer = ""
        for btn in self.option_buttons:
            if btn.isChecked():
                answer = btn.text()
                break
        if answer == "":
            self.feedback.setObjectName("FeedbackBad")
            self.feedback.setText("请先选择一个选项")
            self._repolish(self.feedback)
            return
        self._grade(answer)

    def _grade(self, answer: str) -> None:
        word_id = self.service.word_id_of(self.current)
        result = self.service.submit_answer(
            self.user_id, word_id, self.mode, answer
        )
        self.answered_flag = True

        if result["is_correct"]:
            self.feedback.setObjectName("FeedbackOk")
            self.feedback.setText(
                "✓ 正确！下次复习：{0} 天后".format(result["interval_days"])
            )
        elif result["error_type"] == "confusion":
            self.feedback.setObjectName("FeedbackBad")
            self.feedback.setText(
                "✗ 形近词混淆。正确拼写：{0}（{1}）".format(
                    result["correct_spelling"], result["correct_meaning"])
            )
        elif result["error_type"] == "meaning":
            self.feedback.setObjectName("FeedbackBad")
            self.feedback.setText(
                "✗ 词义错误。正确释义：{0}".format(result["correct_meaning"])
            )
        else:
            self.feedback.setObjectName("FeedbackBad")
            self.feedback.setText(
                "✗ 拼写失误（编辑距离 {0}）。正确拼写：{1}".format(
                    result["edit_distance"], result["correct_spelling"])
            )
        self._repolish(self.feedback)
        self.submit_btn.setEnabled(False)
        self.next_btn.setEnabled(True)
        self.answered.emit(result)

    @staticmethod
    def _repolish(widget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)