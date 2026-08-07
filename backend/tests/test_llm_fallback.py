import os
import types
import unittest
from unittest.mock import patch

from google.api_core import exceptions as google_exceptions

from backend.app.services import llm_backup


class FakeModel:
    def start_chat(self, history=None):
        return self

    def send_message(self, content, **kwargs):
        raise google_exceptions.ResourceExhausted("quota exceeded")


class GenerateReplyFallbackTests(unittest.TestCase):
    def test_generate_reply_returns_fallback_for_quota_exhausted(self):
        fake_genai = types.SimpleNamespace(
            GenerativeModel=lambda *args, **kwargs: FakeModel(),
            types=types.SimpleNamespace(
                GenerationConfig=lambda **kwargs: kwargs),
        )

        with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy"}, clear=False), patch.object(llm_backup, "genai", fake_genai):
            reply = llm_backup.generate_reply([{"role": "user", "content": "hello"}])

        self.assertEqual(
            reply, "The AI service is currently unavailable. Please try again later.")


if __name__ == "__main__":
    unittest.main()
