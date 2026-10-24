"""错词本 Tab：错词列表 + 可视化图表 + 错词强化练习。"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.error_analyzer import label_for
from app.ui.chart_widget import ChartWidget
from app.ui.quiz_widget import QuizWidget


class ErrorBookTab(QWidget):
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

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        # ---- 概览页 ----
        overview = QWidget()
        ov_layout = QVBoxLayout(overview)
        ov_layout.setContentsMargins(0, 0, 0, 0)

        bar = QHBoxLayout()
        self.summary = QLabel("错词统计")
        self.summary.setObjectName("HeaderSub")
        bar.addWidget(self.summary)
        bar.addStretch(1)
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setObjectName("Secondary")
        self.refresh_btn.clicked.connect(self.refresh)
        self.drill_btn = QPushButton("开始强化错词")
        self.drill_btn.clicked.connect(self._start_drill)
        bar.addWidget(self.refresh_btn)
        bar.addWidget(self.drill_btn)
        ov_layout.addLayout(bar)

        body = QHBoxLayout()
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["单词", "释义", "错误类型", "错误次数", "状态"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        body.addWidget(self.table, 3)

        self.chart = ChartWidget()
        body.addWidget(self.chart, 2)
        ov_layout.addLayout(body)

        # ---- 强化练习页 ----
        self.drill_page = QWidget()
        drill_layout = QVBoxLayout(self.drill_page)
        drill_layout.setContentsMargins(0, 0, 0, 0)
        top = QHBoxLayout()
        self.drill_title = QLabel("错词强化练习")
        top.addWidget(self.drill_title)
        top.addStretch(1)
        back_btn = QPushButton("返回错词本")
        back_btn.setObjectName("Secondary")
        back_btn.clicked.connect(self._back_to_overview)
        top.addWidget(back_btn)
        drill_layout.addLayout(top)
        self.drill_quiz = QuizWidget(self.service, self.user_id)
        self.drill_quiz.answered.connect(lambda _res: self.progress.emit())
        drill_layout.addWidget(self.drill_quiz, 1)
        self._drill_words = []

        self.stack.addWidget(overview)
        self.stack.addWidget(self.drill_page)

        self.refresh()

    # ---------- 数据刷新 ----------
    def refresh(self) -> None:
        rows = self.service.error_list(self.user_id, include_resolved=False)
        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(row["spelling"]))
            self.table.setItem(r, 1, QTableWidgetItem(row["meaning_cn"]))
            self.table.setItem(r, 2, QTableWidgetItem(label_for(row["error_type"])))
            self.table.setItem(r, 3, QTableWidgetItem(str(row["error_count"])))
            self.table.setItem(r, 4, QTableWidgetItem("已攻克" if row["resolved"] else "待巩固"))

        self.summary.setText("未攻克错词：{0} 个".format(len(rows)))
        self.chart.render(
            self.service.error_type_chart(self.user_id),
            self.service.weak_word_ranking(self.user_id),
        )
        self._drill_words = rows

    def _start_drill(self) -> None:
        if not self._drill_words:
            self.summary.setText("暂无错词可强化，先去学习吧")
            return
        self.drill_quiz.set_mode("spell")
        self.drill_quiz.start(list(self._drill_words))
        self.stack.setCurrentIndex(1)

    def _back_to_overview(self) -> None:
        self.stack.setCurrentIndex(0)
        self.refresh()

    def switch_to_overview(self) -> None:
        self.stack.setCurrentIndex(0)