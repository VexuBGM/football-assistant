from typing import Optional

from .models import ParseResult
from .nlu import RegexNLU
from .router import ChatbotRouter


class Chatbot:
    def __init__(self, intents_path: Optional[str] = None):
        self.nlu = RegexNLU(intents_path=intents_path)
        self.router = ChatbotRouter()

    def parse(self, text: str) -> ParseResult:
        return self.nlu.parse(text)

    def handle(self, parsed: ParseResult) -> str:
        return self.router.handle(parsed)


__all__ = ["Chatbot", "ParseResult"]
