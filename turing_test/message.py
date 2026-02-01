from PySide6.QtWidgets import (
	QWidget,
	QLabel,
	QHBoxLayout,
	QVBoxLayout,
	QSizePolicy,
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainterPath, QRegion


class MessageWidget(QWidget):
	def __init__(self, text: str, sender: str = "other", timestamp: QDateTime | None = None, parent=None):
		super().__init__(parent)
		self._text = text
		self._sender = sender
		self._timestamp = timestamp or QDateTime.currentDateTime()
		self._init_ui()

	def _init_ui(self) -> None:
		outer = QHBoxLayout(self)
		outer.setContentsMargins(8, 4, 8, 4)
		outer.setSpacing(6)

		bubble = QLabel(self._text)
		bubble.setObjectName("messageBubble")
		bubble.setWordWrap(True)
		bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
		bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
		bubble.setMaximumWidth(420)

		time_lbl = QLabel(self._timestamp.toString("HH:mm"))
		time_lbl.setAlignment(Qt.AlignRight | Qt.AlignBottom)
		time_lbl.setStyleSheet("color: gray; font-size: 10px;")

		vbox = QVBoxLayout()
		vbox.setContentsMargins(0, 0, 0, 0)
		vbox.setSpacing(4)
		vbox.addWidget(bubble)
		vbox.addWidget(time_lbl, 0, Qt.AlignRight)

		if self._sender == "me":
			# name the widget to allow QSS targeting
			self.setObjectName("message_me")
			outer.addStretch()
			outer.addLayout(vbox)
			bubble.setStyleSheet(
				"background-color: #dcf8c6; border-radius: 10px; padding:8px;"
			)
		else:
			# name the widget to allow QSS targeting
			self.setObjectName("message_other")
			outer.addLayout(vbox)
			outer.addStretch()
			bubble.setStyleSheet(
				"background-color: #ffffff; border:1px solid #e0e0e0; border-radius:10px; padding:8px;"
			)

		self.setLayout(outer)

	@property
	def sender(self) -> str:
		return self._sender

	@property
	def text(self) -> str:
		return self._text

	@property
	def timestamp(self) -> QDateTime:
		return self._timestamp
