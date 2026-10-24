"""实验5 - 中学生英语单词智能记忆与错词分析系统（桌面版）

程序启动入口。负责初始化数据库并拉起 PySide6 主窗口。
"""
import sys


def main() -> int:
    from app.db.database import init_db
    from app.db.seed_data import seed_if_empty

    init_db()
    seed_if_empty()

    from PySide6.QtWidgets import QApplication
    from app.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("单词智能记忆系统")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())