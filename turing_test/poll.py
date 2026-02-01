from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout
from PySide6.QtCore import Signal, Qt, QEvent


class PollWidget(QWidget):
    choiceMade = Signal(int)
    hoverChanged = Signal(int, bool)

    def __init__(self, left_text: str, right_text: str, parent=None):
        super().__init__(parent)
        self.left_text = left_text
        self.right_text = right_text
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        lbl = QLabel("Scegli quale risposta è di Giocatore 2:")
        lbl.setAlignment(Qt.AlignCenter)

        row = QHBoxLayout()
        self.btn_left = QPushButton("Risposta 1")
        self.btn_right = QPushButton("Risposta 2")

        self.btn_left.clicked.connect(lambda: self._on_choice(0))
        self.btn_right.clicked.connect(lambda: self._on_choice(1))

        self.btn_left.installEventFilter(self)
        self.btn_right.installEventFilter(self)

        row.addWidget(self.btn_left)
        row.addWidget(self.btn_right)

        layout.addWidget(lbl)
        layout.addLayout(row)

    def _preview(self, text: str) -> str:
        t = text.strip().replace('\n', ' ')
        if len(t) > 80:
            return t[:77] + '...'
        return t

    def _on_choice(self, idx: int):
        self.btn_left.setDisabled(True)
        self.btn_right.setDisabled(True)
        self.choiceMade.emit(idx)

    def eventFilter(self, watched, event):
        if watched is self.btn_left:
            if event.type() == QEvent.Enter:
                self.hoverChanged.emit(0, True)
            elif event.type() == QEvent.Leave:
                self.hoverChanged.emit(0, False)
        elif watched is self.btn_right:
            if event.type() == QEvent.Enter:
                self.hoverChanged.emit(1, True)
            elif event.type() == QEvent.Leave:
                self.hoverChanged.emit(1, False)
        return super().eventFilter(watched, event)
