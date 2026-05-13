from src import clubs_service, db, leagues_service
from src.ai import ai_service


def _seed_clubs(names=("Alpha FC", "Beta FC", "Gamma FC", "Delta FC")):
    for index, name in enumerate(names, start=1):
        clubs_service.add_club(name, f"City {index}", 2000 + index)


def _club_id(name: str) -> int:
    row = db.fetch_one("SELECT id FROM clubs WHERE name = ?", (name,))
    return int(row["id"])


def _create_league(name: str = "Parva Liga", season: str = "2025/2026"):
    leagues_service.create_league(name, season)
    for club_name in ("Alpha FC", "Beta FC", "Gamma FC", "Delta FC"):
        leagues_service.add_team_to_league(club_name, name, season)
    return leagues_service.find_league(name, season)


def _insert_match(
    league_id: int,
    home: str,
    away: str,
    home_goals: int,
    away_goals: int,
    round_no: int,
) -> None:
    db.execute(
        """
        INSERT INTO matches (
          league_id, round_no, home_club_id, away_club_id, home_goals, away_goals, status
        )
        VALUES (?, ?, ?, ?, ?, ?, 'played')
        """,
        (league_id, round_no, _club_id(home), _club_id(away), home_goals, away_goals),
    )


def _seed_prediction_data():
    _seed_clubs()
    league = _create_league()
    league_id = int(league["id"])
    matches = [
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
    ]
    for round_no, (home, away, home_goals, away_goals) in enumerate(matches, start=1):
        _insert_match(league_id, home, away, home_goals, away_goals, round_no)


class TestAIService:
    def test_prediction_with_enough_data_returns_three_valid_probabilities(self):
        _seed_prediction_data()

        prediction, error = ai_service.predict_match("Alpha FC", "Beta FC")

        assert error is None
        assert prediction is not None
        assert prediction.home_team == "Alpha FC"
        assert prediction.away_team == "Beta FC"
        assert prediction.total_probability == 100
        assert prediction.home_win >= 0
        assert prediction.draw >= 0
        assert prediction.away_win >= 0
        assert prediction.features.home.matches_played >= 5
        assert prediction.features.away.matches_played >= 5

    def test_prediction_format_contains_required_output_lines(self):
        _seed_prediction_data()

        result = ai_service.format_prediction("Alpha FC", "Beta FC")

        assert "Прогноза за Alpha FC срещу Beta FC" in result
        assert "Победа Alpha FC:" in result
        assert "Равен:" in result
        assert "Победа Beta FC:" in result

    def test_prediction_with_less_than_five_matches_returns_error(self):
        _seed_clubs()
        league = _create_league()
        _insert_match(int(league["id"]), "Alpha FC", "Beta FC", 2, 1, 1)

        prediction, error = ai_service.predict_match("Alpha FC", "Beta FC")

        assert prediction is None
        assert error is not None
        assert "поне 5 изиграни мача" in error

    def test_prediction_for_missing_team_returns_error(self):
        _seed_prediction_data()

        prediction, error = ai_service.predict_match("Alpha FC", "Missing FC")

        assert prediction is None
        assert error == 'Отборът "Missing FC" не съществува.'

    def test_prediction_for_teams_in_different_leagues_returns_error(self):
        clubs_service.add_club("Alpha FC", "Sofia", 2001)
        clubs_service.add_club("Beta FC", "Plovdiv", 2002)
        leagues_service.create_league("First League", "2025/2026")
        leagues_service.create_league("Second League", "2025/2026")
        leagues_service.add_team_to_league("Alpha FC", "First League", "2025/2026")
        leagues_service.add_team_to_league("Beta FC", "Second League", "2025/2026")

        prediction, error = ai_service.predict_match("Alpha FC", "Beta FC")

        assert prediction is None
        assert error is not None
        assert "не са в една и съща лига" in error
