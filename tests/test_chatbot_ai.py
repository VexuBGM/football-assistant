from src import clubs_service, db, leagues_service
from src.chatbot import Chatbot


def _club_id(name: str) -> int:
    row = db.fetch_one("SELECT id FROM clubs WHERE name = ?", (name,))
    return int(row["id"])


def _seed_chatbot_prediction_data() -> None:
    for name in ("Alpha FC", "Beta FC", "Gamma FC", "Delta FC"):
        clubs_service.add_club(name, "Test City", 2000)
    leagues_service.create_league("Parva Liga", "2025/2026")
    for name in ("Alpha FC", "Beta FC", "Gamma FC", "Delta FC"):
        leagues_service.add_team_to_league(name, "Parva Liga", "2025/2026")

    league = leagues_service.find_league("Parva Liga", "2025/2026")
    league_id = int(league["id"])
    for round_no, (home, away, home_goals, away_goals) in enumerate(
        [
            ("Alpha FC", "Beta FC", 2, 1),
            ("Alpha FC", "Gamma FC", 3, 0),
            ("Delta FC", "Alpha FC", 1, 1),
            ("Alpha FC", "Delta FC", 2, 0),
            ("Gamma FC", "Alpha FC", 0, 2),
            ("Beta FC", "Gamma FC", 1, 1),
            ("Delta FC", "Beta FC", 2, 0),
            ("Beta FC", "Delta FC", 2, 2),
            ("Gamma FC", "Beta FC", 0, 1),
            ("Beta FC", "Alpha FC", 1, 3),
        ],
        start=1,
    ):
        db.execute(
            """
            INSERT INTO matches (
              league_id, round_no, home_club_id, away_club_id, home_goals, away_goals, status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'played')
            """,
            (league_id, round_no, _club_id(home), _club_id(away), home_goals, away_goals),
        )


class TestChatbotAI:
    def test_parse_prediction_english(self):
        parsed = Chatbot().parse("prediction Alpha FC vs Beta FC")

        assert parsed.intent == "predict_match"
        assert parsed.entities == {"home_team": "Alpha FC", "away_team": "Beta FC"}

    def test_parse_prediction_bulgarian(self):
        parsed = Chatbot().parse("Прогноза Alpha FC срещу Beta FC")

        assert parsed.intent == "predict_match"
        assert parsed.entities == {"home_team": "Alpha FC", "away_team": "Beta FC"}

    def test_handle_prediction_command(self):
        _seed_chatbot_prediction_data()
        bot = Chatbot()

        result = bot.handle(bot.parse("prediction Alpha FC vs Beta FC"))

        assert "Прогноза за Alpha FC срещу Beta FC" in result
        assert "Победа Alpha FC:" in result
        assert "Равен:" in result
        assert "Победа Beta FC:" in result

    def test_help_includes_ai_prediction(self):
        result = Chatbot().handle(Chatbot().parse("help"))

        assert "AI Prediction" in result
        assert "prediction <home team> vs <away team>" in result
