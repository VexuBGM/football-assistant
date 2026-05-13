from .models import ParseResult
from ..ai.ai_service import format_prediction
from ..services import clubs_service, leagues_service, matches_service, players_service, standings_service, transfers_service


class ChatbotRouter:
    def __init__(self) -> None:
        self.current_league: dict[str, str] | None = None
        self.current_match_id: int | None = None

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
                    "=== Leagues ===",
                    "- create league <name> <season>",
                    "- add team <club> to league <name> <season>",
                    "- show teams in league <name> <season>",
                    "- remove team <club> from league <name> <season>",
                    "- generate schedule <name> <season>",
                    "=== Matches ===",
                    "- select league <name> <season>",
                    "- show round <number> <league> <season>",
                    "- select match <match_id>",
                    "- result <home>-<away> <X>:<Y> save",
                    "- goal <player> <club> <minute>",
                    "- card <player> <club> <Y|R> <minute>",
                    "- show events [match_id]",
                    "=== Standings ===",
                    "- show standings <league> <season>",
                    "- Покажи класиране <лига> <сезон>",
                    "=== AI Prediction ===",
                    "- prediction <home team> vs <away team>",
                    "- Прогноза <отбор1> срещу <отбор2>",
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

        if tag == "create_league":
            return leagues_service.create_league(parsed.entities["name"], parsed.entities["season"])

        if tag == "add_team_to_league":
            return leagues_service.add_team_to_league(
                parsed.entities["club"],
                parsed.entities["league"],
                parsed.entities["season"],
            )

        if tag == "list_league_teams":
            return leagues_service.list_league_teams(
                parsed.entities["league"],
                parsed.entities["season"],
            )

        if tag == "remove_team_from_league":
            return leagues_service.remove_team_from_league(
                parsed.entities["club"],
                parsed.entities["league"],
                parsed.entities["season"],
            )

        if tag == "generate_schedule":
            return leagues_service.generate_schedule(
                parsed.entities["league"],
                parsed.entities["season"],
            )

        if tag == "select_league":
            league = leagues_service.find_league(parsed.entities["league"], parsed.entities["season"])
            if league is None:
                return (
                    f'Няма лига с име "{parsed.entities["league"]}" '
                    f'сезон {parsed.entities["season"]}.'
                )
            self.current_league = {
                "name": str(league["name"]),
                "season": str(league["season"]),
            }
            return (
                f'Selected league "{self.current_league["name"]}" '
                f'season {self.current_league["season"]}.'
            )

        if tag == "show_round":
            return matches_service.show_round(
                parsed.entities["league"],
                parsed.entities["season"],
                parsed.entities["round_no"],
            )

        if tag == "select_match":
            match_id = parsed.entities["match_id"]
            result = matches_service.select_match(match_id)
            if not result.startswith("No match"):
                self.current_match_id = match_id
            return result

        if tag == "record_result":
            if self.current_league is None:
                return 'Select a league first with "select league <name> <season>".'
            entities = parsed.entities
            return matches_service.record_result(
                self.current_league["name"],
                self.current_league["season"],
                entities["home_team"],
                entities["away_team"],
                entities["home_goals"],
                entities["away_goals"],
            )

        if tag == "add_goal":
            if self.current_match_id is None:
                return 'Select a match first with "select match <match_id>".'
            return matches_service.add_goal_from_text(
                self.current_match_id,
                parsed.entities["subject"],
                parsed.entities["minute"],
            )

        if tag == "add_card":
            if self.current_match_id is None:
                return 'Select a match first with "select match <match_id>".'
            return matches_service.add_card_from_text(
                self.current_match_id,
                parsed.entities["subject"],
                parsed.entities["card_type"],
                parsed.entities["minute"],
            )

        if tag == "show_events":
            match_id = parsed.entities.get("match_id", self.current_match_id)
            if match_id is None:
                return 'Select a match first with "select match <match_id>", or provide a match ID.'
            return matches_service.show_events(match_id)

        if tag == "show_standings":
            return standings_service.format_standings(
                parsed.entities["league"],
                parsed.entities["season"],
            )

        if tag == "predict_match":
            return format_prediction(
                parsed.entities["home_team"],
                parsed.entities["away_team"],
            )

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
