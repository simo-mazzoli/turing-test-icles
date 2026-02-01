from google import genai
import time


class RateLimitError(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit raggiunto. Riprova tra {retry_after} secondi.")


class AIClient:
    MAX_REQUESTS_PER_MINUTE = 15
    RATE_LIMIT_WINDOW = 60

    def __init__(self, api_key: str = "AIzaSyAmFz8g-tJDFL4h1ByIcN0vB3N0aSMFTgc", model_name: str = "gemma-3-27b-it"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)

        self.generation_config = {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 200,
        }

        self._request_timestamps = []

    def _check_rate_limit(self):
        now = time.time()
        self._request_timestamps = [ts for ts in self._request_timestamps if now - ts < self.RATE_LIMIT_WINDOW]
        if len(self._request_timestamps) >= self.MAX_REQUESTS_PER_MINUTE:
            oldest = self._request_timestamps[0]
            retry_after = int(self.RATE_LIMIT_WINDOW - (now - oldest)) + 1
            raise RateLimitError(retry_after)
        self._request_timestamps.append(now)

    def generate_response(self, prompt: str) -> str:
        self._check_rate_limit()
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config,
            )
            text = getattr(response, 'text', None) or str(response)
            return text.strip()
        except RateLimitError:
            raise
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "quota" in error_msg or "429" in error_msg:
                raise RateLimitError(60)
            raise
