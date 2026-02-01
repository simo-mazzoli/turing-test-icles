from PySide6.QtCore import QThread, Signal

class AIWorker(QThread):
    responseReady = Signal(str)

    def __init__(self, prompt: str, parent=None):
        super().__init__(parent)
        self.prompt = prompt

    def run(self):
        try:
            from turing_test.ai_client import AIClient
            client = AIClient()  # uses embedded API key
            text = client.generate_response(self.prompt)
        except Exception:
            text = "(IA) Risposta generata automaticamente: " + (self.prompt[:120] + '...' if len(self.prompt) > 120 else self.prompt)

        try:
            self.responseReady.emit(text)
        except Exception:
            pass
