from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QHBoxLayout,
    QPushButton,
)
from PySide6.QtCore import Signal


class PlayerResponseDialog(QDialog):
    """Dialog shown to Player 2 to enter their response.

    Usage:
        dlg = PlayerResponseDialog(question_text)
        if dlg.exec_() == QDialog.Accepted:
            response = dlg.response_text
    """

    responseSubmitted = Signal(str)

    def __init__(self, question: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Player 2 — Your response")
        self.response_text = ""
        self._init_ui(question)

    def _init_ui(self, question: str):
        layout = QVBoxLayout(self)

        lbl = QLabel(question)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Write your answer here...")
        self.text_edit.setFixedHeight(180)

        btn_row = QHBoxLayout()
        btn_submit = QPushButton("Submit")
        btn_cancel = QPushButton("Cancel")

        btn_row.addStretch()
        btn_row.addWidget(btn_submit)
        btn_row.addWidget(btn_cancel)

        layout.addWidget(lbl)
        layout.addWidget(self.text_edit)
        layout.addLayout(btn_row)

        btn_submit.clicked.connect(self._on_submit)
        btn_cancel.clicked.connect(self.reject)

    def _on_submit(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            return
        self.response_text = text
        self.responseSubmitted.emit(text)
        self.accept()
