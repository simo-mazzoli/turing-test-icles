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
    QPlainTextEdit,
    QHBoxLayout,
    QMessageBox,
    QDialog,
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QFile, QTextStream, QTimer, QSettings

from turing_test.fsm import StateMachine
from turing_test.message import MessageWidget
from turing_test.player_response import PlayerResponseDialog
from turing_test.ai_worker import AIWorker
from turing_test.poll import PollWidget
import random

import rc_images
import rc_icons
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

        self._icon_pixmap = QPixmap(":/icons/icon.ico")
        self.setWindowIcon(QIcon(self._icon_pixmap))

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
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.setContentsMargins(20, 20, 20, 20)

        # Prompt template field
        lbl_prompt = QLabel("Prompt template per l'AI:")
        lbl_prompt.setStyleSheet("font-weight:600;")
        self._settings_prompt_edit = QPlainTextEdit()
        self._settings_prompt_edit.setFixedHeight(140)
        self._settings_prompt_edit.setPlaceholderText('Usa {question}, {length} e {answer} come segnaposto')

        # API key field (with show/hide toggle)
        lbl_api = QLabel("API Key:")
        lbl_api.setStyleSheet("font-weight:600;")
        self._settings_api_key_edit = QLineEdit()
        self._settings_api_key_edit.setEchoMode(QLineEdit.Password)
        self._settings_api_key_edit.setPlaceholderText('Inserisci la chiave API per il servizio AI')
        btn_toggle_api = QPushButton("Mostra")
        btn_toggle_api.setFixedSize(80, 28)
        btn_toggle_api.setObjectName('btnToggleApi')
        btn_toggle_api.clicked.connect(lambda: self._toggle_api_visibility(btn_toggle_api))

        # Buttons
        btn_save = QPushButton("Salva")
        btn_save.setObjectName("btnSaveSettings")
        btn_save.setFixedSize(120, 40)
        btn_save.clicked.connect(self._save_settings)

        # preview button removed

        btn_back = QPushButton("Back")
        btn_back.setObjectName("btnBack")
        btn_back.setFixedSize(120, 40)
        btn_back.clicked.connect(self._fsm.go_to_main_menu.emit)

        # Filler
        layout.addStretch(2)

        layout.addWidget(lbl_prompt)
        layout.addWidget(self._settings_prompt_edit)
        layout.addSpacing(8)
        layout.addWidget(lbl_api)
        h_api = QHBoxLayout()
        h_api.addWidget(self._settings_api_key_edit)
        h_api.addSpacing(8)
        h_api.addWidget(btn_toggle_api)
        layout.addLayout(h_api)
        layout.addSpacing(12)
        hl = QHBoxLayout()
        hl.addStretch(1)
        hl.addWidget(btn_save)
        hl.addSpacing(8)
        hl.addWidget(btn_back)
        layout.addLayout(hl)
        layout.addSpacing(20)

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

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("whiteContainer")
        scroll.setStyleSheet(self._load_stylesheet(":/styles/container_full.qss"))
        messages_container = QWidget()
        messages_container.setStyleSheet("background: transparent;")
        messages_layout = QVBoxLayout(messages_container)
        messages_layout.setContentsMargins(6, 6, 6, 6)
        messages_layout.setSpacing(6)
        messages_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(messages_container)

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
        input_layout.setStretch(0, 1)
        input_layout.addWidget(send_btn)
        input_layout.addSpacing(12)
        input_layout.addWidget(menu_btn)

        layout.addSpacing(120)
        layout.addWidget(scroll)
        layout.addWidget(input_container)

        def append_message(text: str, sender: str = "other"):
            if not text:
                return
            msg = MessageWidget(text, sender)
            messages_layout.addWidget(msg)
            messages_container.adjustSize()
            scroll.ensureWidgetVisible(msg)
            
        def on_send():
            text = line_edit.text().strip()
            if not text:
                return
            append_message(text, "me")
            line_edit.clear()
            round_id = self._round_counter = self._round_counter + 1
            self._pending_rounds[round_id] = {"question": text, "ai": None, "human": None, "worker": None}

            dlg = PlayerResponseDialog(text, parent=self)
            if dlg.exec() == QDialog.Accepted:
                resp = dlg.response_text
                # register human response first so we can compute its length
                self._on_human_ready(round_id, resp)

                # start AI worker after human response, passing human response length and the human answer
                ai_worker = AIWorker(text, parent=self, human_length=len(resp), human_answer=resp)
                self._pending_rounds[round_id]["worker"] = ai_worker
                ai_worker.responseReady.connect(lambda r, rid=round_id: self._on_ai_ready(rid, r))
                ai_worker.errorOccurred.connect(lambda err, rid=round_id: self._show_error_popup(err))
                ai_worker.start()
            else:
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
        try:
            settings = QSettings("TuringTest", "TuringTestApp")
            prompt = settings.value('ai/prompt_template', '', type=str) or ''
            api_key = settings.value('ai/api_key', '', type=str) or ''
            if hasattr(self, '_settings_prompt_edit'):
                self._settings_prompt_edit.setPlainText(prompt)
            if hasattr(self, '_settings_api_key_edit'):
                self._settings_api_key_edit.setText(api_key)
                # ensure API key field is hidden by default when opening settings
                try:
                    self._settings_api_key_edit.setEchoMode(QLineEdit.Password)
                except Exception:
                    pass
        except Exception:
            pass

    def _save_settings(self):
        try:
            settings = QSettings("TuringTest", "TuringTestApp")
            prompt = ''
            api_key = ''
            if hasattr(self, '_settings_prompt_edit'):
                prompt = self._settings_prompt_edit.toPlainText().strip()
            if hasattr(self, '_settings_api_key_edit'):
                api_key = self._settings_api_key_edit.text().strip()

            missing_question = '{question}' not in prompt
            missing_length = '{length}' not in prompt

            if missing_question or missing_length:
                msg = 'Il template dovrebbe contenere i segnaposto {question} e {length}.'
                if missing_question and missing_length:
                    QMessageBox.warning(self, 'Template non valido', msg + '\nSalvataggio annullato.')
                    return
                # If only one is missing, warn but allow user to proceed
                reply = QMessageBox.question(self, 'Template incompleto', msg + '\nVuoi comunque salvare?', QMessageBox.Yes | QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return

            settings.setValue('ai/prompt_template', prompt)
            settings.setValue('ai/api_key', api_key)
        except Exception:
            pass

    def _toggle_api_visibility(self, btn: QPushButton):
        try:
            if self._settings_api_key_edit.echoMode() == QLineEdit.Password:
                self._settings_api_key_edit.setEchoMode(QLineEdit.Normal)
                btn.setText('Nascondi')
            else:
                self._settings_api_key_edit.setEchoMode(QLineEdit.Password)
                btn.setText('Mostra')
        except Exception:
            pass

    # preview removed
    
    def on_gamerules_entered(self):
        self._stacked_widget.setCurrentIndex(2)

    def on_gameplay_entered(self):
        self._stacked_widget.setCurrentIndex(3)

    def _show_error_popup(self, error_text: str):
        try:
            dlg = QDialog(self)
            dlg.setWindowTitle("Errore");
            dlg.setModal(False)
            dlg.setFixedSize(520, 240)

            layout = QVBoxLayout(dlg)
            title = QLabel("Errore nel servizio AI")
            title.setStyleSheet("font-weight:700; font-size:16px; color: #ffffff;")
            title.setAlignment(Qt.AlignLeft)

            code_label = QLabel(error_text)
            code_label.setWordWrap(True)
            code_label.setStyleSheet(
                "background: #2b2b2b; color: #f1f1f1; padding: 10px; border-radius: 6px; font-family: monospace; font-size:12px;"
            )

            btn_close = QPushButton("Chiudi")
            btn_close.setFixedSize(100, 32)
            btn_close.clicked.connect(dlg.accept)

            layout.addWidget(title)
            layout.addWidget(code_label)
            layout.addStretch(1)
            hl = QHBoxLayout()
            hl.addStretch(1)
            hl.addWidget(btn_close)
            layout.addLayout(hl)

            # Apply container styling if available
            try:
                dlg.setStyleSheet(self._load_stylesheet(":/styles/container.qss") + " QDialog { background: rgba(40,40,40,0.95); }")
            except Exception:
                pass

            dlg.show()
        except Exception:
            pass

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

        ai_text = pending.get("ai")
        human_text = pending.get("human")

        try:
            gp_widget = self._gameplay_widget
            scroll = gp_widget.findChild(QScrollArea)
            if scroll:
                container = scroll.widget()
                messages_layout = None
                for child in container.children():
                    if hasattr(child, 'layout'):
                        pass
                messages_layout = container.layout()
                if messages_layout is None:
                    return
                choices = [(human_text, "human"), (ai_text, "ai")]
                random.shuffle(choices)

                msg_widgets = []
                for text, role in choices:
                    w = MessageWidget(text, "other")
                    messages_layout.addWidget(w)
                    msg_widgets.append((w, role))

                poll = PollWidget(choices[0][0], choices[1][0])
                messages_layout.addWidget(poll)

                correct_index = 0 if choices[0][1] == "human" else 1
                poll.choiceMade.connect(lambda idx, rid=round_id, p=poll, m=msg_widgets, ci=correct_index: self._on_poll_choice(rid, idx, p, m, ci))

                def _on_hover(idx, entering, m=msg_widgets):
                    try:
                        w, role = m[idx]
                        bubble = w.findChild(QLabel, "messageBubble")
                        if bubble is None:
                            return
                        if not hasattr(bubble, '_orig_style'):
                            bubble._orig_style = bubble.styleSheet()
                        if entering:
                            bubble.setStyleSheet(bubble._orig_style + "background-color: rgba(70,130,180,0.06);")
                        else:
                            bubble.setStyleSheet(bubble._orig_style)
                    except Exception:
                        pass

                poll.hoverChanged.connect(_on_hover)
                try:
                    scroll.ensureWidgetVisible(poll)
                except Exception:
                    QTimer.singleShot(0, lambda: scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum()))
        finally:
            try:
                self._pending_rounds.pop(round_id, None)
            except Exception:
                pass

    def _on_poll_choice(self, round_id: int, choice_idx: int, poll_widget, msg_widgets, correct_index: int):
        for i, (w, role) in enumerate(msg_widgets):
            bubble = w.findChild(QLabel, "messageBubble")
            if bubble is None:
                continue
            # Ensure we have a stored original style used by hover handling
            if not hasattr(bubble, '_orig_style'):
                bubble._orig_style = bubble.styleSheet()

            if i == correct_index:
                # apply green border and make it part of the stored original style
                new_style = bubble._orig_style + "border: 3px solid #28a745;"
                bubble._orig_style = new_style
                bubble.setStyleSheet(new_style)
            if i == choice_idx and i != correct_index:
                # apply red border for the (incorrect) chosen answer
                new_style = bubble._orig_style + "border: 3px solid #e53935;"
                bubble._orig_style = new_style
                bubble.setStyleSheet(new_style)

