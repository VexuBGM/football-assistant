# src/chatbot.py
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Optional

from . import clubs_service


@dataclass
class ParseResult:
    intent: str
    entities: dict[str, Any]


class Chatbot:
    def __init__(self, intents_path: Optional[str] = None):
        if intents_path is None:
            intents_path = os.path.join(os.path.dirname(__file__), "intents.json")

        with open(intents_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.intents = data.get("intents", [])

        # предварително компилираме regex
        self._compiled = []
        for intent in self.intents:
            tag = intent["tag"]
            for p in intent.get("patterns", []):
                self._compiled.append((tag, re.compile(p, re.IGNORECASE)))

    def parse(self, text: str) -> ParseResult:
        t = text.strip()
        for tag, rgx in self._compiled:
            m = rgx.match(t)
            if m:
                # entities според intent
                if tag == "add_club":
                    name = m.group(1).strip()
                    city = m.group(2).strip()
                    year = m.group(3)
                    return ParseResult(tag, {"name": name, "city": city, "founded_year": int(year) if year else None})

                if tag == "delete_club":
                    ident = m.group(1).strip()
                    return ParseResult(tag, {"identifier": ident})

                return ParseResult(tag, {})
        return ParseResult("unknown", {})

    def handle(self, parsed: ParseResult) -> str:
        if parsed.intent == "help":
            return (
                "Команди:\n"
                "- Добави клуб <име> <град> [година]\n"
                "- Покажи всички клубове\n"
                "- Изтрий клуб <име|id>\n"
                "- помощ\n"
                "- изход"
            )

        if parsed.intent == "add_club":
            return clubs_service.add_club(
                parsed.entities["name"],
                parsed.entities["city"],
                parsed.entities.get("founded_year"),
            )

        if parsed.intent == "list_clubs":
            return clubs_service.get_all_clubs()

        if parsed.intent == "delete_club":
            return clubs_service.delete_club(parsed.entities["identifier"])

        if parsed.intent == "exit":
            return "EXIT"

        if parsed.intent == "unknown":
            return "🤖 Не разбрах. Напиши „помощ“ за списък с команди."

        return "❌ Вътрешна грешка: непознат intent."
