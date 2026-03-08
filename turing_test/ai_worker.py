from PySide6.QtCore import QThread, Signal, QSettings
import traceback


class AIWorker(QThread):
    responseReady = Signal(str)
    errorOccurred = Signal(str)

    def __init__(self, prompt: str, parent=None, human_length: int = None, human_answer: str = None):
        super().__init__(parent)
        self.prompt = prompt
        self.human_length = human_length
        self.human_answer = human_answer

    def run(self):
        try:
            # Build the prompt template; allow override from settings
            lunghezza = self.human_length or 120
            settings = QSettings("TuringTest", "TuringTestApp")
            template = settings.value('ai/prompt_template', '', type=str) or ''
            # tolerate common typos for backwards-compat
            # no automatic correction for 'ansrew' typo
            if template:
                try:
                    testoPrompt = template.format(question=self.prompt, length=lunghezza, answer=self.human_answer or '')
                except Exception:
                    testoPrompt = template.replace('{question}', self.prompt).replace('{length}', str(lunghezza)).replace('{answer}', self.human_answer or '')
            else:
                testoPrompt = f"""
Il giocatore A sta giocando al turing test. Ha la possibilità di porre una domanda: "{self.prompt}". 
Tu devi rispondere in modo indistinguibile da un essere umano.
La tua risposta deve essere lunga circa {lunghezza} caratteri (simile alla risposta del destinatario).
Evita l'uso di emoji e qualsiasi formattazione testuale (grassetto, corsivo, sottolineato o markup). Rispondi in testo semplice.
"""

            from turing_test.ai_client import AIClient
            api_key = settings.value('ai/api_key', '', type=str) or None
            if api_key:
                client = AIClient(api_key=api_key)
            else:
                client = AIClient()
            text = client.generate_response(testoPrompt)
        except Exception as e:
            err = traceback.format_exc()
            try:
                self.errorOccurred.emit(err)
            except Exception:
                pass
            fallback = self.prompt or "(nessuna domanda)"
            text = "(IA) Risposta generata automaticamente: " + (fallback[:120] + '...' if len(fallback) > 120 else fallback)

        try:
            self.responseReady.emit(text)
        except Exception:
            pass
