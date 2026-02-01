from PySide6.QtCore import QThread, Signal

class AIWorker(QThread):
    responseReady = Signal(str)

    def __init__(self, prompt: str, parent=None, human_length: int = None):
        super().__init__(parent)
        self.prompt = prompt
        self.human_length = human_length

    def run(self):
        try:
            # Build the same prompt template used in the legacy Google Apps Script
            lunghezza = self.human_length or 120
            testoPrompt = f"""
Il giocatore A sta giocando al turing test. Ha la possibilità di porre una domanda: "{self.prompt}". 
Tu devi rispondere in modo indistinguibile da un essere umano.
La tua risposta deve essere lunga circa {lunghezza} caratteri (simile alla risposta del destinatario).
"""

            from turing_test.ai_client import AIClient
            client = AIClient()  # uses embedded API key
            text = client.generate_response(testoPrompt)
        except Exception:
            fallback = self.prompt or "(nessuna domanda)"
            text = "(IA) Risposta generata automaticamente: " + (fallback[:120] + '...' if len(fallback) > 120 else fallback)

        try:
            self.responseReady.emit(text)
        except Exception:
            pass
