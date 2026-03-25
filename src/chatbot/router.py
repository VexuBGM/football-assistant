from .models import ParseResult
from ..services import clubs_service, players_service, transfers_service


class ChatbotRouter:
    def handle(self, parsed: ParseResult) -> str:
        tag = parsed.intent

        if tag == "help":
            return "\n".join(
                [
                    "Commands:",
                    "=== Clubs ===",
                    "- add club <name> <city> [year]",
                    "- list clubs",
                    "- delete club <name|id>",
                    "=== Players ===",
                    "- add player <name> in <club> position <GK|DF|MF|FW> number <1-99> born <date> nat <nationality>",
                    "- list players of <club> / list players",
                    "- change number of <player> to <number>",
                    "- change position of <player> to <position>",
                    "- change status of <player> to <status>",
                    "- delete player <name|id>",
                    "- seed players",
                    "=== Transfers ===",
                    "- transfer <player> from <club> to <club> YYYY-MM-DD [fee <amount>]",
                    "- show transfers of <player>",
                    "- show transfers of club <club>",
                    "- seed transfers",
                    "=== Other ===",
                    "- help",
                    "- exit",
                ]
            )

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
            entities = parsed.entities
            return players_service.add_player(
                entities["full_name"],
                entities["club"],
                entities["position"],
                entities["number"],
                entities["birth_date"],
                entities["nationality"],
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

        if tag == "transfer_player":
            entities = parsed.entities
            return transfers_service.transfer_player(
                entities["player_name"],
                entities.get("from_club"),
                entities["to_club"],
                entities["date"],
                entities.get("fee"),
            )

        if tag == "show_transfers_player":
            return transfers_service.list_transfers_by_player(parsed.entities["name"])

        if tag == "show_transfers_club":
            return transfers_service.list_transfers_by_club(parsed.entities["name"])

        if tag == "seed_transfers":
            return transfers_service.seed_transfer_history()

        if tag == "exit":
            return "EXIT"

        if tag == "unknown":
            return 'I did not understand. Type "help" for a list of commands.'

        return "Internal error: unknown intent."
