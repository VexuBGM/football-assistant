from src import clubs_service, db, leagues_service, standings_service


def _seed_league():
    for name, city in (
        ("Alpha FC", "Sofia"),
        ("Beta FC", "Plovdiv"),
        ("Gamma FC", "Varna"),
        ("Delta FC", "Burgas"),
    ):
        clubs_service.add_club(name, city, 2000)

    leagues_service.create_league("Parva Liga", "2025/2026")
    for club_name in ("Alpha FC", "Beta FC", "Gamma FC", "Delta FC"):
        leagues_service.add_team_to_league(club_name, "Parva Liga", "2025/2026")

    return leagues_service.find_league("Parva Liga", "2025/2026")


def _club_id(name: str) -> int:
    row = db.fetch_one("SELECT id FROM clubs WHERE name = ?", (name,))
    return int(row["id"])


def _insert_match(
    league_id: int,
    home_name: str,
    away_name: str,
    home_goals: int | None = None,
    away_goals: int | None = None,
    status: str = "scheduled",
    round_no: int = 1,
) -> None:
    db.execute(
        """
        INSERT INTO matches (
          league_id, round_no, home_club_id, away_club_id, home_goals, away_goals, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (league_id, round_no, _club_id(home_name), _club_id(away_name), home_goals, away_goals, status),
    )


def _row_by_team(rows, team_name: str):
    return next(row for row in rows if row.team == team_name)


class TestStandingsService:
    def test_league_without_played_matches_returns_zero_table(self):
        _seed_league()

        result = standings_service.format_standings("Parva Liga", "2025/2026")

        assert "Няма изиграни мачове" in result
        assert "1. Alpha FC 0 0 0 0 0:0 0 0" in result
        assert "4. Gamma FC 0 0 0 0 0:0 0 0" in result

    def test_one_played_match_calculates_points_and_goals(self):
        league = _seed_league()
        _insert_match(int(league["id"]), "Alpha FC", "Beta FC", 2, 1, "played")

        rows, error = standings_service.calculate_standings("Parva Liga", "2025/2026")

        assert error is None
        alpha = _row_by_team(rows, "Alpha FC")
        beta = _row_by_team(rows, "Beta FC")
        gamma = _row_by_team(rows, "Gamma FC")
        assert (alpha.mp, alpha.wins, alpha.gf, alpha.ga, alpha.gd, alpha.points) == (1, 1, 2, 1, 1, 3)
        assert (beta.mp, beta.losses, beta.gf, beta.ga, beta.gd, beta.points) == (1, 1, 1, 2, -1, 0)
        assert (gamma.mp, gamma.points) == (0, 0)

    def test_multiple_matches_accumulate_statistics(self):
        league = _seed_league()
        _insert_match(int(league["id"]), "Alpha FC", "Beta FC", 2, 1, "played", 1)
        _insert_match(int(league["id"]), "Gamma FC", "Alpha FC", 1, 1, "played", 2)

        rows, error = standings_service.calculate_standings("Parva Liga", "2025/2026")

        assert error is None
        alpha = _row_by_team(rows, "Alpha FC")
        gamma = _row_by_team(rows, "Gamma FC")
        assert (alpha.mp, alpha.wins, alpha.draws, alpha.losses, alpha.gf, alpha.ga, alpha.points) == (
            2,
            1,
            1,
            0,
            3,
            2,
            4,
        )
        assert (gamma.mp, gamma.draws, gamma.points) == (1, 1, 1)

    def test_equal_points_sort_by_goal_difference_then_goals_for(self):
        league = _seed_league()
        _insert_match(int(league["id"]), "Alpha FC", "Delta FC", 2, 0, "played", 1)
        _insert_match(int(league["id"]), "Beta FC", "Gamma FC", 3, 1, "played", 1)

        rows, error = standings_service.calculate_standings("Parva Liga", "2025/2026")

        assert error is None
        assert [row.team for row in rows[:2]] == ["Beta FC", "Alpha FC"]
        assert rows[0].points == rows[1].points == 3
        assert rows[0].gd == rows[1].gd == 2
        assert rows[0].gf > rows[1].gf

    def test_scheduled_match_with_score_is_ignored(self):
        league = _seed_league()
        _insert_match(int(league["id"]), "Alpha FC", "Beta FC", 5, 0, "scheduled")

        rows, error = standings_service.calculate_standings("Parva Liga", "2025/2026")

        assert error is None
        assert all(row.mp == 0 and row.points == 0 for row in rows)

    def test_missing_league_returns_clear_error(self):
        result = standings_service.format_standings("Missing Liga", "2025/2026")

        assert 'Няма лига с име "Missing Liga" сезон 2025/2026.' == result

    def test_match_with_team_outside_league_returns_consistency_error(self):
        league = _seed_league()
        clubs_service.add_club("Outsider FC", "Ruse", 2001)
        _insert_match(int(league["id"]), "Alpha FC", "Outsider FC", 1, 0, "played")

        result = standings_service.format_standings("Parva Liga", "2025/2026")

        assert "Грешка в данните" in result
        assert "извън league_teams" in result
