# src/chatbot.py
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Optional

from . import clubs_service
from . import players_service


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
                if tag == "add_club":
                    name = m.group(1).strip()
                    city = m.group(2).strip()
                    year = m.group(3)
                    return ParseResult(tag, {
                        "name": name, "city": city,
                        "founded_year": int(year) if year else None,
                    })

                if tag == "delete_club":
                    return ParseResult(tag, {"identifier": m.group(1).strip()})

                if tag == "add_player":
                    return ParseResult(tag, {
                        "full_name": m.group(1).strip(),
                        "club": m.group(2).strip(),
                        "position": m.group(3).strip(),
                        "number": int(m.group(4)),
                        "birth_date": m.group(5).strip(),
                        "nationality": m.group(6).strip(),
                    })

                if tag == "list_players":
                    club = None
                    for i in range(1, len(m.groups()) + 1):
                        g = m.group(i)
                        if g:
                            club = g.strip()
                            break
                    return ParseResult(tag, {"club": club})

                if tag == "update_player_number":
                    return ParseResult(tag, {
                        "player_name": m.group(1).strip(),
                        "number": int(m.group(2)),
                    })

                if tag == "update_player_position":
                    return ParseResult(tag, {
                        "player_name": m.group(1).strip(),
                        "position": m.group(2).strip(),
                    })

                if tag == "update_player_status":
                    return ParseResult(tag, {
                        "player_name": m.group(1).strip(),
                        "status": m.group(2).strip(),
                    })

                if tag == "delete_player":
                    return ParseResult(tag, {"identifier": m.group(1).strip()})

                return ParseResult(tag, {})
        return ParseResult("unknown", {})

    def handle(self, parsed: ParseResult) -> str:
        tag = parsed.intent

        if tag == "help":
            lines = [
                "Commands:",
                "=== Clubs ===",
                "- add club <name> <city> [year]",
                "- list clubs",
                "- delete club <name|id>",
                "=== Players ===",
                "- add player <name> in <club> position <GK|DF|MF|FW> number <1-99> born <date> nat <nationality>",
                "- list players of <club>  /  list all players",
                "- change number of <player> to <number>",
                "- change position of <player> to <position>",
                "- change status of <player> to <status>",
                "- delete player <name|id>",
                "- seed players",
                "=== Other ===",
                "- help",
                "- exit",
            ]
            return "\n".join(lines)

        if tag == "add_club":
            return clubs_service.add_club(
                parsed.entities["name"],
                parsed.entities["city"],
                parsed.entities.get("founded_year"),
            )

        if tag == "list_clubs":
            return clubs_service.get_all_clubs()

        if tag == "delete_club":
            return clubs_service.delete_club(parsed.entities["identifier"])

        if tag == "add_player":
            e = parsed.entities
            return players_service.add_player(
                e["full_name"], e["club"], e["position"],
                e["number"], e["birth_date"], e["nationality"],
            )

        if tag == "list_players":
            return players_service.list_players(parsed.entities.get("club"))

        if tag == "update_player_number":
            return players_service.update_player(
                parsed.entities["player_name"],
                number=parsed.entities["number"],
            )

        if tag == "update_player_position":
            return players_service.update_player(
                parsed.entities["player_name"],
                position=parsed.entities["position"],
            )

        if tag == "update_player_status":
            return players_service.update_player(
                parsed.entities["player_name"],
                status=parsed.entities["status"],
            )

        if tag == "delete_player":
            return players_service.delete_player(parsed.entities["identifier"])

        if tag == "seed_players":
            return players_service.seed_test_data()

        if tag == "exit":
            return "EXIT"

        if tag == "unknown":
            return 'I did not understand. Type "help" for a list of commands.'

        return "Internal error: unknown intent."
