from PySide6.QtWidgets import (
    QMainWindow,
    QSizePolicy,
    QLabel,
    QStackedWidget,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QScrollArea,
    QLineEdit,
    QHBoxLayout,
    QDialog,
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QFile, QTextStream, QTimer

from turing_test.fsm import StateMachine
from turing_test.message import MessageWidget
from turing_test.player_response import PlayerResponseDialog
from turing_test.ai_worker import AIWorker
from turing_test.poll import PollWidget
import random

import rc_images
# import rc_icons
import rc_styles

class MainWindow(QMainWindow):

    __MAIN_WINDOW_TITLE     = "Turing Test"
    __MAIN_WINDOW_WIDTH     = 1280
    __MAIN_WINDOW_HEIGHT    = 720

    @staticmethod
    def _load_stylesheet(path):
        file = QFile(path)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            stylesheet = stream.readAll()
            file.close()
            return stylesheet
        return ""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.__MAIN_WINDOW_TITLE)
        self.setGeometry(100, 100, self.__MAIN_WINDOW_WIDTH, self.__MAIN_WINDOW_HEIGHT)
        self.setFixedSize(self.__MAIN_WINDOW_WIDTH, self.__MAIN_WINDOW_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self._background_label = QLabel(self)
        self._background_label.setScaledContents(True)
        self._background_label.setAlignment(Qt.AlignCenter)
        self._background_pixmap = QPixmap(":/images/background.png")
        self._background_label.setGeometry(0, 0, self.__MAIN_WINDOW_WIDTH, self.__MAIN_WINDOW_HEIGHT)
        self._background_label.setPixmap(self._background_pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        ))

        # self._icon_pixmap = QPixmap(":/icons/icon.ico")
        # self.setWindowIcon(QIcon(self._icon_pixmap))

        self._stacked_widget = QStackedWidget(self)
        self._stacked_widget.setGeometry(0, 0, self.__MAIN_WINDOW_WIDTH, self.__MAIN_WINDOW_HEIGHT)

        self._logo_label = QLabel(self)
        logo_pixmap = QPixmap(":/images/testa.png")
        scaled_logo = logo_pixmap.scaledToHeight(300, Qt.SmoothTransformation)
        self._logo_label.setPixmap(scaled_logo)
        logo_x = (self.__MAIN_WINDOW_WIDTH - scaled_logo.width()) // 2
        self._logo_label.setGeometry(logo_x, 0, scaled_logo.width(), scaled_logo.height())
        self._logo_label.raise_()
        
        self._fsm = StateMachine(self)

        self._main_menu_widget  = self._create_main_menu_widget()
        self._settings_widget   = self._create_settings_widget()
        self._gamerules_widget  = self._create_gamerules_widget()
        self._gameplay_widget   = self._create_gameplay_widget()
        
        self._stacked_widget.addWidget(self._main_menu_widget)  # index 0
        self._stacked_widget.addWidget(self._settings_widget)   # index 1
        self._stacked_widget.addWidget(self._gamerules_widget)  # index 2
        self._stacked_widget.addWidget(self._gameplay_widget)   # index 3
        
        self._fsm.state_main_menu.entered.connect(self.on_main_menu_entered)
        self._fsm.state_settings.entered.connect(self.on_settings_entered)
        self._fsm.state_gamerules.entered.connect(self.on_gamerules_entered)
        self._fsm.state_gameplay.entered.connect(self.on_gameplay_entered)
        
        self._fsm.start()
        # tracking for question rounds: id -> {question, ai, human, worker}
        self._round_counter = 0
        self._pending_rounds = {}

    def _create_main_menu_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        btn_start = QPushButton("Start Game")
        btn_start.setObjectName("btnStartGame")
        btn_start.setMinimumSize(200, 50)
        btn_start.clicked.connect(self._fsm.go_to_gamerules.emit)
        
        btn_settings = QPushButton("Settings")
        btn_settings.setObjectName("btnSettings")
        btn_settings.setMinimumSize(200, 50)
        btn_settings.clicked.connect(self._fsm.go_to_settings.emit)
        
        btn_exit = QPushButton("Exit")
        btn_exit.setObjectName("btnExit")
        btn_exit.setMinimumSize(200, 50)
        btn_exit.clicked.connect(self.close)
        
        layout.addStretch(3)
        layout.addWidget(btn_start)
        layout.addWidget(btn_settings)
        layout.addWidget(btn_exit)
        layout.addStretch(1)
        
        return widget
    
    def _create_settings_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        layout.setContentsMargins(20, 20, 20, 20)
        
        btn_back = QPushButton("Back")
        btn_back.setObjectName("btnBack")
        btn_back.setMinimumSize(120, 50)
        btn_back.clicked.connect(self._fsm.go_to_main_menu.emit)
        
        layout.addWidget(btn_back)
        
        return widget
    
    def _create_gamerules_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        container = QWidget()
        container.setObjectName("whiteContainer")
        container.setStyleSheet(self._load_stylesheet(":/styles/container.qss"))
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(20)
        container_layout.setAlignment(Qt.AlignCenter)
        
        label_rules = QLabel("Il giocatore 1 scrive la domanda da porre a giocatore 2 e all'IA. Nella nuova finestra che si aprirà, giocatore 2 dovrà dare la sua risposta. Nella finestra pricipale, giocatore 1 dovrà scegliere quale tra le due risposte è quella data da giocatore 2.")
        label_rules.setAlignment(Qt.AlignCenter)
        label_rules.setWordWrap(True)
        label_rules.setFixedWidth(600)
        label_rules.setStyleSheet("color: #333; font-size: 16px;")

        btn_start_gameplay = QPushButton("Start Playing")
        btn_start_gameplay.setObjectName("btnStartGame")
        btn_start_gameplay.setFixedSize(200, 50)
        btn_start_gameplay.clicked.connect(self._fsm.go_to_gameplay.emit)
        
        btn_back = QPushButton("Back")
        btn_back.setObjectName("btnBack")
        btn_back.setFixedSize(200, 50)
        btn_back.clicked.connect(self._fsm.go_to_main_menu.emit)
        
        container_layout.addWidget(label_rules)
        container_layout.addWidget(btn_start_gameplay)
        container_layout.addWidget(btn_back)
        
        layout.addWidget(container)
        
        return widget
    
    def _create_gameplay_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 0)
        layout.setSpacing(8)

        # Scrollable message area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("whiteContainer")
        scroll.setStyleSheet(self._load_stylesheet(":/styles/container_full.qss"))
        messages_container = QWidget()
        # ensure the container itself is transparent so the scroll area's rounded
        # background masks any edges
        messages_container.setStyleSheet("background: transparent;")
        messages_layout = QVBoxLayout(messages_container)
        messages_layout.setContentsMargins(6, 6, 6, 6)
        messages_layout.setSpacing(6)
        messages_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(messages_container)

        # Input area (styled like the white container)
        input_container = QWidget()
        input_container.setObjectName("whiteContainer")
        input_container.setStyleSheet(self._load_stylesheet(":/styles/container.qss"))
        input_container.setFixedHeight(100)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(16, 12, 16, 0)
        input_layout.setSpacing(0)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Type your question or a message...")
        line_edit.setMinimumHeight(40)
        send_btn = QPushButton("Send")
        send_btn.setObjectName("btnSend")
        menu_btn = QPushButton("Back to menu")
        menu_btn.setObjectName("btnBackFromGameplay")

        input_layout.addWidget(line_edit)
        # make the line edit expand and push buttons to the right
        input_layout.setStretch(0, 1)
        input_layout.addWidget(send_btn)
        input_layout.addSpacing(12)
        input_layout.addWidget(menu_btn)

        # add a spacer above the scroll area so it doesn't start at the very top
        layout.addSpacing(120)
        layout.addWidget(scroll)
        layout.addWidget(input_container)

        def append_message(text: str, sender: str = "other"):
            if not text:
                return
            msg = MessageWidget(text, sender)
            messages_layout.addWidget(msg)
            # force layout update and ensure the new widget is visible
            messages_container.adjustSize()
            scroll.ensureWidgetVisible(msg)
            
        def on_send():
            text = line_edit.text().strip()
            if not text:
                return
            append_message(text, "me")
            line_edit.clear()
            # create a new round and start AI worker
            round_id = self._round_counter = self._round_counter + 1
            self._pending_rounds[round_id] = {"question": text, "ai": None, "human": None, "worker": None}

            ai_worker = AIWorker(text, parent=self)
            # keep reference so it doesn't get GC'd
            self._pending_rounds[round_id]["worker"] = ai_worker
            ai_worker.responseReady.connect(lambda r, rid=round_id: self._on_ai_ready(rid, r))
            ai_worker.start()

            # open a dialog for Player 2 to enter their response
            dlg = PlayerResponseDialog(text, parent=self)
            # modal: wait for player 2
            if dlg.exec() == QDialog.Accepted:
                resp = dlg.response_text
                # store human response and maybe commit both messages
                self._on_human_ready(round_id, resp)
            else:
                # player cancelled: drop the pending round (AI result will be ignored)
                try:
                    self._pending_rounds.pop(round_id, None)
                except Exception:
                    pass

        send_btn.clicked.connect(on_send)
        line_edit.returnPressed.connect(on_send)
        menu_btn.clicked.connect(self._fsm.go_to_main_menu.emit)

        return widget

    def on_main_menu_entered(self):
        self._stacked_widget.setCurrentIndex(0)

    def on_settings_entered(self):
        self._stacked_widget.setCurrentIndex(1)
    
    def on_gamerules_entered(self):
        self._stacked_widget.setCurrentIndex(2)

    def on_gameplay_entered(self):
        self._stacked_widget.setCurrentIndex(3)

    def _on_ai_ready(self, round_id: int, text: str):
        pending = self._pending_rounds.get(round_id)
        if not pending:
            return
        pending["ai"] = text
        self._maybe_commit_round(round_id)

    def _on_human_ready(self, round_id: int, text: str):
        pending = self._pending_rounds.get(round_id)
        if not pending:
            return
        pending["human"] = text
        self._maybe_commit_round(round_id)

    def _maybe_commit_round(self, round_id: int):
        pending = self._pending_rounds.get(round_id)
        if not pending:
            return
        if pending.get("ai") is None or pending.get("human") is None:
            return

        # both ready: append human and ai as distinct messages
        ai_text = pending.get("ai")
        human_text = pending.get("human")

        # find append_message in the gameplay widget scope: recreate minimal logic
        # (we'll reuse the same append_message used earlier by calling the layout API)
        try:
            # access the current gameplay widget's scroll and layout
            # locate the scroll area we created earlier by walking children
            gp_widget = self._gameplay_widget
            scroll = gp_widget.findChild(QScrollArea)
            if scroll:
                container = scroll.widget()
                messages_layout = None
                for child in container.children():
                    if hasattr(child, 'layout'):
                        # the messages_layout is the QVBoxLayout of the container
                        pass
                # safe fallback: use addWidget on container's layout
                messages_layout = container.layout()
                if messages_layout is None:
                    return
                # create two choices and shuffle them so player must guess
                choices = [(human_text, "human"), (ai_text, "ai")]
                random.shuffle(choices)

                msg_widgets = []
                for text, role in choices:
                    w = MessageWidget(text, "other")
                    messages_layout.addWidget(w)
                    msg_widgets.append((w, role))

                # add poll below the two messages
                poll = PollWidget(choices[0][0], choices[1][0])
                messages_layout.addWidget(poll)

                # determine which index corresponds to the human response
                correct_index = 0 if choices[0][1] == "human" else 1
                poll.choiceMade.connect(lambda idx, rid=round_id, p=poll, m=msg_widgets, ci=correct_index: self._on_poll_choice(rid, idx, p, m, ci))

                # highlight corresponding message on hover
                def _on_hover(idx, entering, m=msg_widgets):
                    try:
                        w, role = m[idx]
                        bubble = w.findChild(QLabel, "messageBubble")
                        if bubble is None:
                            return
                        # store original style once
                        if not hasattr(bubble, '_orig_style'):
                            bubble._orig_style = bubble.styleSheet()
                        if entering:
                            bubble.setStyleSheet(bubble._orig_style + "background-color: rgba(70,130,180,0.06);")
                        else:
                            bubble.setStyleSheet(bubble._orig_style)
                    except Exception:
                        pass

                poll.hoverChanged.connect(_on_hover)
                # ensure visible (scroll to bottom)
                try:
                    scroll.ensureWidgetVisible(poll)
                except Exception:
                    QTimer.singleShot(0, lambda: scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum()))
        finally:
            # clean up pending
            try:
                self._pending_rounds.pop(round_id, None)
            except Exception:
                pass

    def _on_poll_choice(self, round_id: int, choice_idx: int, poll_widget, msg_widgets, correct_index: int):
        # mark messages: green for correct, red for incorrect selection
        for i, (w, role) in enumerate(msg_widgets):
            bubble = w.findChild(QLabel, "messageBubble")
            if bubble is None:
                continue
            if i == correct_index:
                # correct answer
                bubble.setStyleSheet(bubble.styleSheet() + "border: 3px solid #28a745;")
            if i == choice_idx and i != correct_index:
                # chosen wrong answer
                bubble.setStyleSheet(bubble.styleSheet() + "border: 3px solid #e53935;")

