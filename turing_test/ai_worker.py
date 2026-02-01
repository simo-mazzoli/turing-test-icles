from PySide6.QtCore import QThread, Signal

class AIWorker(QThread):
    """Background worker that asks the AI for a response and emits it.

    Tries to use google.genai Client if available; falls back to a canned response.
    """
    responseReady = Signal(str)

    def __init__(self, prompt: str, parent=None):
        super().__init__(parent)
        self.prompt = prompt

    def run(self):
        # try to call google.genai if available
        try:
            from turing_test.ai_client import AIClient
            client = AIClient()  # uses embedded API key
            text = client.generate_response(self.prompt)
        except Exception:
            # fallback canned reply
            text = "(IA) Risposta generata automaticamente: " + (self.prompt[:120] + '...' if len(self.prompt) > 120 else self.prompt)

        # emit whatever text we have
        try:
            self.responseReady.emit(text)
        except Exception:
            pass
