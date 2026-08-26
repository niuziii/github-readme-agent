import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from config import AppConfig
from ui import STYLESHEET, MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("GitHub 项目解读 Agent")
    app.setStyleSheet(STYLESHEET)

    font = app.font()
    font.setFamily("Microsoft YaHei UI")
    font.setPointSize(10)
    app.setFont(font)

    window = MainWindow(AppConfig())
    window.show()

    if "--screenshot" in sys.argv:
        index = sys.argv.index("--screenshot")
        path = sys.argv[index + 1] if len(sys.argv) > index + 1 else "screenshot.png"

        def capture() -> None:
            window.grab().save(path)
            app.quit()

        QTimer.singleShot(900, capture)
    elif "--smoke-test" in sys.argv:
        QTimer.singleShot(400, app.quit)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
