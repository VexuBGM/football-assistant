import json
import os
import re
from typing import Optional

from .models import ParseResult


def _guess_transfers_history_intent(command_text: str, target: str) -> str:
    lowered_command = command_text.lower()
    if "играч" in lowered_command or "player" in lowered_command:
        return "show_transfers_player"
    if "клуб" in lowered_command or "club" in lowered_command:
        return "show_transfers_club"

    token_count = len(target.split())
    return "show_transfers_club" if token_count == 1 else "show_transfers_player"


class RegexNLU:
    def __init__(self, intents_path: Optional[str] = None):
        if intents_path is None:
            intents_path = os.path.join(os.path.dirname(__file__), "intents.json")

        with open(intents_path, "r", encoding="utf-8") as intents_file:
            data = json.load(intents_file)

        self.intents = data.get("intents", [])
        self._compiled: list[tuple[str, re.Pattern[str]]] = []
        for intent in self.intents:
            for pattern in intent.get("patterns", []):
                self._compiled.append((intent["tag"], re.compile(pattern, re.IGNORECASE)))

    def parse(self, text: str) -> ParseResult:
        command = " ".join(text.strip().split())
        if not command:
            return ParseResult("unknown", {})

        for tag, pattern in self._compiled:
            match = pattern.match(command)
            if not match:
                continue

            if tag == "add_club":
                year = match.group(3)
                return ParseResult(
                    "add_club",
                    {
                        "name": match.group(1).strip(),
                        "city": match.group(2).strip(),
                        "founded_year": int(year) if year else None,
                    },
                )

            if tag == "delete_club":
                return ParseResult("delete_club", {"identifier": match.group(1).strip()})

            if tag == "add_player":
                return ParseResult(
                    "add_player",
                    {
                        "full_name": match.group(1).strip(),
                        "club": match.group(2).strip(),
                        "position": match.group(3).strip(),
                        "number": int(match.group(4)),
                        "birth_date": match.group(5).strip(),
                        "nationality": match.group(6).strip(),
                    },
                )

            if tag == "list_players":
                club = None
                for group_index in range(1, len(match.groups()) + 1):
                    value = match.group(group_index)
                    if value:
                        club = value.strip()
                        break
                return ParseResult("list_players", {"club": club})

            if tag == "update_player_number":
                return ParseResult(
                    "update_player_number",
                    {
                        "player_name": match.group(1).strip(),
                        "number": int(match.group(2)),
                    },
                )

            if tag == "update_player_position":
                return ParseResult(
                    "update_player_position",
                    {
                        "player_name": match.group(1).strip(),
                        "position": match.group(2).strip(),
                    },
                )

            if tag == "update_player_status":
                return ParseResult(
                    "update_player_status",
                    {
                        "player_name": match.group(1).strip(),
                        "status": match.group(2).strip(),
                    },
                )

            if tag == "delete_player":
                return ParseResult("delete_player", {"identifier": match.group(1).strip()})

            if tag == "transfer_player":
                if len(match.groups()) == 5:
                    return ParseResult(
                        "transfer_player",
                        {
                            "player_name": match.group(1).strip(),
                            "from_club": match.group(2).strip(),
                            "to_club": match.group(3).strip(),
                            "date": match.group(4).strip(),
                            "fee": match.group(5).strip() if match.group(5) else None,
                        },
                    )

                return ParseResult(
                    "transfer_player",
                    {
                        "player_name": match.group(1).strip(),
                        "from_club": "",
                        "to_club": match.group(2).strip(),
                        "date": match.group(3).strip(),
                        "fee": match.group(4).strip() if match.group(4) else None,
                    },
                )

            if tag in {"show_transfers_player", "show_transfers_club"}:
                target = match.group(1).strip()
                resolved_tag = _guess_transfers_history_intent(command, target) if tag == "show_transfers_player" else tag
                return ParseResult(resolved_tag, {"name": target})

            return ParseResult(tag, {})

        return ParseResult("unknown", {})
