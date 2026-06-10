from src import db
from src.ai.ai_service import predict_match
from src.services import seed_service
from src.services.standings_service import calculate_standings


def _count(table: str) -> int:
    row = db.fetch_one(f"SELECT COUNT(*) AS count FROM {table}")
    return int(row["count"])


class TestSeedService:
    def test_full_demo_seed_creates_data_for_all_features(self):
        result = seed_service.seed_full_demo_data()

        assert result.startswith("Full demo seed loaded:")
        assert _count("clubs") == 6
        assert _count("players") == 24
        assert _count("leagues") == 2
        assert _count("league_teams") == 12
        assert _count("matches") == 30
        assert _count("goals") == 5
        assert _count("cards") == 3
        assert _count("transfers") == 3

    def test_full_demo_seed_is_idempotent(self):
        seed_service.seed_full_demo_data()
        first_counts = {table: _count(table) for table in ["clubs", "players", "matches", "goals", "cards", "transfers"]}

        result = seed_service.seed_full_demo_data()
        second_counts = {
            table: _count(table) for table in ["clubs", "players", "matches", "goals", "cards", "transfers"]
        }

        assert result == "Full demo seed is already loaded."
        assert second_counts == first_counts

    def test_clear_database_removes_seeded_data_and_resets_ids(self):
        seed_service.seed_full_demo_data()

        result = seed_service.clear_database()
        cleared_counts = {
            table: _count(table)
            for table in ["clubs", "players", "leagues", "league_teams", "matches", "goals", "cards", "transfers"]
        }

        assert result == "Database cleared: 85 rows removed."
        assert all(count == 0 for count in cleared_counts.values())

        seed_service.seed_full_demo_data()
        first_club = db.fetch_one("SELECT id FROM clubs ORDER BY id LIMIT 1")

        assert int(first_club["id"]) == 1

    def test_clear_database_is_idempotent(self):
        result = seed_service.clear_database()

        assert result == "Database is already empty."

    def test_seed_supports_standings_prediction_and_scheduled_match_testing(self):
        seed_service.seed_full_demo_data()

        standings, error = calculate_standings(seed_service.DEMO_LEAGUE, seed_service.DEMO_SEASON)
        prediction, prediction_error = predict_match("Levski Sofia", "CSKA Sofia")
        scheduled = db.fetch_one("SELECT COUNT(*) AS count FROM matches WHERE status = 'scheduled'")

        assert error is None
        assert len(standings) == 6
        assert all(row.mp == 5 for row in standings)
        assert prediction_error is None
        assert prediction is not None
        assert prediction.total_probability == 100
        assert int(scheduled["count"]) == 15
