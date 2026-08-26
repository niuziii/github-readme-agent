"""PySide6 桌面界面：简洁高级的暗色对话窗口。"""

from __future__ import annotations

import markdown
from PySide6.QtCore import QPoint, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizeGrip,
    QSpinBox,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from agent import AnalysisWorker
from config import AppConfig


STYLESHEET = """
QWidget {
    font-family: "Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
    color: #D6DFE8;
}
QMainWindow, QDialog {
    background: transparent;
}
#rootPanel {
    background: #0F141A;
    border: 1px solid #232B35;
    border-radius: 14px;
}
#windowTitle {
    color: #F2F6FA;
    font-size: 16px;
    font-weight: 600;
}
#windowSubtitle {
    color: #7F8B96;
    font-size: 11px;
}
#windowBtn, #windowCloseBtn {
    background: transparent;
    color: #9AA7B3;
    border: none;
    border-radius: 7px;
    font-size: 14px;
}
#windowBtn:hover {
    background: #1B232D;
    color: #E6EDF3;
}
#windowCloseBtn:hover {
    background: #B34035;
    color: #FFFFFF;
}
#urlEdit {
    background: #0A0E13;
    border: 1px solid #252E39;
    border-radius: 9px;
    padding: 9px 12px;
    color: #E6EDF3;
    font-size: 13px;
    selection-background-color: #1B3A36;
}
#urlEdit:focus {
    border: 1px solid #2DD4BF;
}
#urlEdit:disabled {
    color: #5D6A76;
}
#primaryBtn {
    background: #14B8A6;
    color: #07110F;
    border: none;
    border-radius: 9px;
    padding: 0 22px;
    font-weight: 600;
    font-size: 13px;
}
#primaryBtn:hover {
    background: #2DD4BF;
}
#primaryBtn:disabled {
    background: #173D38;
    color: #4E7A72;
}
#iconBtn {
    background: #17202A;
    border: 1px solid #26303B;
    border-radius: 9px;
    color: #9AA7B3;
    font-size: 15px;
}
#iconBtn:hover {
    border-color: #2DD4BF;
    color: #E6EDF3;
}
#ghostBtn {
    background: transparent;
    border: 1px solid #2A333D;
    border-radius: 8px;
    color: #B8C4CE;
    padding: 6px 14px;
}
#ghostBtn:hover {
    border-color: #2DD4BF;
    color: #5EEAD4;
}
#ghostBtn:disabled {
    color: #46525E;
    border-color: #202832;
}
#dangerBtn {
    background: transparent;
    border: 1px solid #7A2E28;
    border-radius: 8px;
    color: #F2A99F;
    padding: 6px 14px;
}
#dangerBtn:hover {
    background: #3A1D1B;
    border-color: #D9534F;
}
#output {
    background: #0A0E13;
    border: 1px solid #1E2732;
    border-radius: 10px;
    padding: 10px;
    selection-background-color: #1B3A36;
}
#statusLabel {
    color: #7F8B96;
    font-size: 12px;
}
#statusLabel[error="true"] {
    color: #F2998F;
}
#repoLabel {
    color: #2DD4BF;
    font-size: 12px;
    font-weight: 600;
}
#settingsDialog {
    background: #121820;
    border-radius: 12px;
}
#dialogTitle {
    color: #F2F6FA;
    font-size: 15px;
    font-weight: 600;
}
#hintLabel {
    color: #6F7C88;
    font-size: 12px;
}
QDialog QLineEdit, QDialog QDoubleSpinBox, QDialog QSpinBox {
    background: #0A0E13;
    border: 1px solid #252E39;
    border-radius: 8px;
    padding: 7px 10px;
    color: #E6EDF3;
}
QDialog QLineEdit:focus {
    border: 1px solid #2DD4BF;
}
QDialogButtonBox QPushButton {
    background: #17202A;
    border: 1px solid #2A333D;
    border-radius: 8px;
    color: #D6DFE8;
    padding: 7px 18px;
    min-width: 80px;
}
QDialogButtonBox QPushButton:hover {
    border-color: #2DD4BF;
    color: #5EEAD4;
}
QToolTip {
    background: #111820;
    color: #D6DFE8;
    border: 1px solid #2A333D;
    padding: 5px 8px;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #2A333D;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #3A4754;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""


MARKDOWN_CSS = """
body {
    font-family: "Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
    color: #D6DFE8;
}
h1, h2, h3 {
    color: #F2F6FA;
    font-weight: 600;
}
h1 {
    font-size: 20px;
    margin: 6px 0 12px;
}
h2 {
    font-size: 16px;
    margin: 18px 0 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #252D37;
}
h3 {
    font-size: 14px;
    margin: 14px 0 6px;
}
p {
    margin: 6px 0;
    line-height: 1.6;
}
ul, ol {
    margin: 6px 0 8px;
    padding-left: 22px;
}
li {
    margin: 3px 0;
    line-height: 1.55;
}
code {
    background: #1C242E;
    color: #7FE0CF;
    border-radius: 4px;
    padding: 1px 5px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px;
}
pre {
    background: #0B0F14;
    border: 1px solid #222A34;
    border-radius: 8px;
    padding: 10px 12px;
    margin: 8px 0;
}
pre code {
    background: transparent;
    color: #D9E2EC;
    padding: 0;
}
blockquote {
    border-left: 3px solid #2DD4BF;
    margin: 8px 0;
    padding: 4px 12px;
    color: #A9B6C2;
    background: #121922;
    border-radius: 0 6px 6px 0;
}
a {
    color: #5EEAD4;
    text-decoration: none;
}
table {
    border-collapse: collapse;
    margin: 8px 0;
}
th, td {
    border: 1px solid #29323D;
    padding: 5px 10px;
}
th {
    background: #182029;
    color: #E6EDF3;
}
"""


def render_markdown(text: str) -> str:
    body = markdown.markdown(
        text or "", extensions=["fenced_code", "tables", "sane_lists"]
    )
    return (
        '<html><head><meta charset="utf-8">'
        f"<style>{MARKDOWN_CSS}</style></head><body>{body}</body></html>"
    )


class Spinner(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(18, 18)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.setInterval(45)
        self._timer.timeout.connect(self._rotate)

    def start(self) -> None:
        self._timer.start()
        self.update()

    def stop(self) -> None:
        self._timer.stop()
        self.update()

    def _rotate(self) -> None:
        self._angle = (self._angle + 30) % 360
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        if not self._timer.isActive():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("#2DD4BF"), 2.5)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(self.rect().adjusted(2, 2, -2, -2), self._angle * 16, 280 * 16)
        painter.end()


class DragHeader(QWidget):
    def __init__(self, window: QMainWindow, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._window = window
        self._drag_offset = QPoint()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._drag_offset = (
                event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if event.buttons() & Qt.LeftButton and not self._drag_offset.isNull():
            self._window.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()


class SettingsDialog(QDialog):
    def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("设置")
        self.setModal(True)
        self.setMinimumWidth(540)
        self.setObjectName("settingsDialog")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(14)

        title = QLabel("模型与 API 设置")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.base_url_edit = QLineEdit(config.base_url)
        self.base_url_edit.setPlaceholderText("OpenAI 兼容地址，例如 https://api.deepseek.com/v1")

        self.api_key_edit = QLineEdit(config.api_key)
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("sk-...")

        self.model_edit = QLineEdit(config.model)
        self.model_edit.setPlaceholderText("例如 deepseek-chat 或 gpt-4o-mini")

        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 2.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setValue(config.temperature)

        self.token_edit = QLineEdit(config.github_token)
        self.token_edit.setEchoMode(QLineEdit.Password)
        self.token_edit.setPlaceholderText("可选，用于提升 GitHub API 限流额度")

        self.max_chars_spin = QSpinBox()
        self.max_chars_spin.setRange(4000, 100000)
        self.max_chars_spin.setSingleStep(1000)
        self.max_chars_spin.setSuffix(" 字符")
        self.max_chars_spin.setValue(config.max_readme_chars)

        form.addRow("LLM API 地址", self.base_url_edit)
        form.addRow("LLM API Key", self.api_key_edit)
        form.addRow("模型名称", self.model_edit)
        form.addRow("温度", self.temp_spin)
        form.addRow("GitHub Token", self.token_edit)
        form.addRow("单段上限", self.max_chars_spin)
        layout.addLayout(form)

        hint = QLabel(
            "API Key 仅保存在本机 .env 文件中，不会上传。GitHub Token 可提升 API 限流额度。"
        )
        hint.setObjectName("hintLabel")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("保存")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self) -> None:
        self.config.save(
            base_url=self.base_url_edit.text().strip(),
            api_key=self.api_key_edit.text().strip(),
            model=self.model_edit.text().strip(),
            temperature=str(self.temp_spin.value()),
            github_token=self.token_edit.text().strip(),
            max_readme_chars=str(self.max_chars_spin.value()),
        )
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.config = config
        self.worker: AnalysisWorker | None = None
        self._markdown_buffer = ""
        self._repo_slug = ""
        self._cancelling = False

        self.setWindowTitle("GitHub 项目解读 Agent")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(900, 620)
        self.resize(980, 700)

        root = QWidget(self)
        root.setObjectName("rootPanel")
        root.setAttribute(Qt.WA_StyledBackground, True)
        self.setCentralWidget(root)

        shadow = QGraphicsDropShadowEffect(root)
        shadow.setBlurRadius(34)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 150))
        root.setGraphicsEffect(shadow)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)
        layout.addWidget(self._build_header())
        layout.addLayout(self._build_input_row())
        layout.addLayout(self._build_status_row())
        layout.addWidget(self._build_output(), 1)
        layout.addLayout(self._build_footer())

        self._render_timer = QTimer(self)
        self._render_timer.setSingleShot(True)
        self._render_timer.setInterval(200)
        self._render_timer.timeout.connect(self._flush_render)

    def _build_header(self) -> QWidget:
        header = DragHeader(self)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(10)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        title = QLabel("GitHub 项目解读 Agent")
        title.setObjectName("windowTitle")
        subtitle = QLabel("粘贴仓库链接 · 智能解析 · 中文解读")
        subtitle.setObjectName("windowSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)
        layout.addStretch(1)

        self.min_btn = self._make_window_button("–", "windowBtn", "最小化")
        self.close_btn = self._make_window_button("✕", "windowCloseBtn", "关闭")
        self.min_btn.clicked.connect(self.showMinimized)
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.min_btn)
        layout.addWidget(self.close_btn)
        return header

    def _make_window_button(self, text: str, object_name: str, tooltip: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setToolTip(tooltip)
        button.setFixedSize(34, 28)
        button.setCursor(Qt.PointingHandCursor)
        return button

    def _build_input_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        self.url_edit = QLineEdit()
        self.url_edit.setObjectName("urlEdit")
        self.url_edit.setPlaceholderText(
            "粘贴 GitHub 仓库链接，例如 https://github.com/openai/openai-python"
        )
        self.url_edit.setClearButtonEnabled(True)
        self.url_edit.setFixedHeight(38)
        self.url_edit.returnPressed.connect(self.start_analysis)
        row.addWidget(self.url_edit, 1)

        self.analyze_btn = QPushButton("开始分析")
        self.analyze_btn.setObjectName("primaryBtn")
        self.analyze_btn.setFixedHeight(38)
        self.analyze_btn.setCursor(Qt.PointingHandCursor)
        self.analyze_btn.clicked.connect(self.start_analysis)
        row.addWidget(self.analyze_btn)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setObjectName("iconBtn")
        self.settings_btn.setFixedSize(40, 38)
        self.settings_btn.setToolTip("设置")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self.open_settings)
        row.addWidget(self.settings_btn)
        return row

    def _build_status_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        self.spinner = Spinner()
        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("statusLabel")
        self.repo_label = QLabel("")
        self.repo_label.setObjectName("repoLabel")
        row.addWidget(self.spinner)
        row.addWidget(self.status_label)
        row.addStretch(1)
        row.addWidget(self.repo_label)
        return row

    def _build_output(self) -> QTextBrowser:
        self.output = QTextBrowser()
        self.output.setObjectName("output")
        self.output.setOpenExternalLinks(True)
        self.output.setPlaceholderText("输入 GitHub 仓库链接后点击「开始分析」，即可获得结构化中文解读")
        return self.output

    def _build_footer(self) -> QHBoxLayout:
        footer = QHBoxLayout()
        footer.setSpacing(8)

        self.repo_link_btn = QPushButton("打开仓库")
        self.repo_link_btn.setObjectName("ghostBtn")
        self.repo_link_btn.setFixedHeight(30)
        self.repo_link_btn.setCursor(Qt.PointingHandCursor)
        self.repo_link_btn.setEnabled(False)
        self.repo_link_btn.clicked.connect(self._open_repository)
        footer.addWidget(self.repo_link_btn)

        self.copy_btn = QPushButton("复制结果")
        self.copy_btn.setObjectName("ghostBtn")
        self.copy_btn.setFixedHeight(30)
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy_result)
        footer.addWidget(self.copy_btn)

        self.cancel_btn = QPushButton("停止")
        self.cancel_btn.setObjectName("dangerBtn")
        self.cancel_btn.setFixedHeight(30)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self._cancel_analysis)
        footer.addWidget(self.cancel_btn)

        footer.addStretch(1)
        grip = QSizeGrip(self.centralWidget())
        grip.setFixedSize(16, 16)
        footer.addWidget(grip)
        return footer

    def start_analysis(self) -> None:
        if self.worker and self.worker.isRunning():
            return

        url = self.url_edit.text().strip()
        if not url:
            self.set_status("请先粘贴 GitHub 仓库链接", error=True)
            return
        if not self.config.api_key or not self.config.base_url:
            self.set_status("请先在设置中配置 LLM API", error=True)
            self.open_settings()
            return

        self._markdown_buffer = ""
        self._repo_slug = ""
        self._render_timer.stop()
        self.output.clear()
        self.repo_label.setText("")
        self.repo_link_btn.setEnabled(False)
        self.cancel_btn.setVisible(True)
        self.url_edit.setEnabled(False)
        self.analyze_btn.setEnabled(False)
        self.spinner.start()
        self.set_status("准备中...")

        self.worker = AnalysisWorker(self.config, url)
        self.worker.status_changed.connect(self.set_status)
        self.worker.repo_ready.connect(self._on_repo_ready)
        self.worker.stream_delta.connect(self._on_stream_delta)
        self.worker.analysis_finished.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def set_status(self, message: str, error: bool = False) -> None:
        self.status_label.setText(message)
        self.status_label.setProperty("error", error)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _on_repo_ready(self, repo: str) -> None:
        self._repo_slug = repo
        self.repo_label.setText(repo)
        self.repo_link_btn.setEnabled(True)
        self.set_status("已识别仓库，正在获取 README...")

    def _on_stream_delta(self, delta: str) -> None:
        self._markdown_buffer += delta
        if not self._render_timer.isActive():
            self._render_timer.start()

    def _flush_render(self) -> None:
        if not self._markdown_buffer:
            return
        scrollbar = self.output.verticalScrollBar()
        previous_value = scrollbar.value()
        self.output.setUpdatesEnabled(False)
        self.output.setHtml(render_markdown(self._markdown_buffer))
        if previous_value > 0 and scrollbar.maximum() > 0:
            scrollbar.setValue(min(previous_value, scrollbar.maximum()))
        self.output.setUpdatesEnabled(True)

    def _on_finished(self, text: str) -> None:
        self._markdown_buffer = text
        self._render_timer.stop()
        self._flush_render()
        self._finish_run(f"分析完成 · {len(text):,} 字")

    def _on_failed(self, message: str) -> None:
        self._render_timer.stop()
        self.output.setHtml(render_markdown(f"### 分析失败\n\n{message}\n\n请检查链接、网络或模型配置后重试。"))
        self._finish_run(message, error=True)

    def _finish_run(self, status: str, error: bool = False) -> None:
        self.spinner.stop()
        self.url_edit.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        self.cancel_btn.setVisible(False)
        self.set_status(status, error=error)

    def _on_worker_finished(self) -> None:
        if self._cancelling:
            self._cancelling = False
            self._render_timer.stop()
            if self._markdown_buffer.strip():
                self._flush_render()
                self._finish_run("已停止分析 · 已保留已生成内容")
            else:
                self.output.setHtml(render_markdown("### 已停止\n\n本次分析已手动停止。"))
                self._finish_run("已停止分析", error=True)
        self.worker = None

    def _cancel_analysis(self) -> None:
        if self.worker and self.worker.isRunning():
            self._cancelling = True
            self.worker.cancel()
            self.set_status("正在停止...")

    def _copy_result(self) -> None:
        text = self.output.toPlainText().strip()
        if not text:
            self.set_status("暂无结果可复制")
            return
        QApplication.clipboard().setText(text)
        self.set_status("结果已复制到剪贴板")

    def _open_repository(self) -> None:
        if self._repo_slug:
            QDesktopServices.openUrl(QUrl(f"https://github.com/{self._repo_slug}"))

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            self.set_status("设置已保存")

    def closeEvent(self, event) -> None:  # noqa: N802
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(1500)
        super().closeEvent(event)
