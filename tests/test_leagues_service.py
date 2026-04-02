from src import clubs_service, db, leagues_service


def _seed_clubs():
    clubs_service.add_club("Levski Sofia", "Sofia", 1914)
    clubs_service.add_club("CSKA Sofia", "Sofia", 1948)
    clubs_service.add_club("Ludogorets", "Razgrad", 2001)
    clubs_service.add_club("Botev Plovdiv", "Plovdiv", 1912)
    clubs_service.add_club("Cherno More", "Varna", 1913)


def _create_league():
    return leagues_service.create_league("Parva Liga", "2025/2026")


class TestLeaguesService:
    def test_create_league_success(self):
        result = _create_league()
        assert "Parva Liga" in result
        assert "2025/2026" in result

    def test_create_league_duplicate(self):
        _create_league()
        result = _create_league()
        assert "already exists" in result

    def test_create_league_invalid_season(self):
        result = leagues_service.create_league("Parva Liga", "2025-2026")
        assert "Invalid season format" in result

    def test_add_team_to_league_success(self):
        _seed_clubs()
        _create_league()
        result = leagues_service.add_team_to_league("Levski Sofia", "Parva Liga", "2025/2026")
        assert "Levski Sofia" in result

    def test_add_team_duplicate(self):
        _seed_clubs()
        _create_league()
        leagues_service.add_team_to_league("Levski Sofia", "Parva Liga", "2025/2026")
        result = leagues_service.add_team_to_league("Levski Sofia", "Parva Liga", "2025/2026")
        assert "вече" in result.lower()

    def test_list_league_teams(self):
        _seed_clubs()
        _create_league()
        leagues_service.add_team_to_league("Levski Sofia", "Parva Liga", "2025/2026")
        leagues_service.add_team_to_league("CSKA Sofia", "Parva Liga", "2025/2026")
        result = leagues_service.list_league_teams("Parva Liga", "2025/2026")
        assert "Levski Sofia" in result
        assert "CSKA Sofia" in result

    def test_remove_team_blocked_after_schedule(self):
        _seed_clubs()
        _create_league()
        for club in ("Levski Sofia", "CSKA Sofia", "Ludogorets", "Botev Plovdiv"):
            leagues_service.add_team_to_league(club, "Parva Liga", "2025/2026")
        leagues_service.generate_schedule("Parva Liga", "2025/2026")
        result = leagues_service.remove_team_from_league("Levski Sofia", "Parva Liga", "2025/2026")
        assert "Не може" in result

    def test_generate_schedule_with_four_teams(self):
        _seed_clubs()
        _create_league()
        for club in ("Levski Sofia", "CSKA Sofia", "Ludogorets", "Botev Plovdiv"):
            leagues_service.add_team_to_league(club, "Parva Liga", "2025/2026")

        result = leagues_service.generate_schedule("Parva Liga", "2025/2026")

        assert "Кръгове: 3" in result
        assert "Мачове: 6" in result

        league = leagues_service.find_league("Parva Liga", "2025/2026")
        count = db.fetch_one("SELECT COUNT(*) AS count FROM matches WHERE league_id = ?", (league["id"],))
        assert count["count"] == 6

    def test_generate_schedule_requires_minimum_teams(self):
        _seed_clubs()
        _create_league()
        for club in ("Levski Sofia", "CSKA Sofia", "Ludogorets"):
            leagues_service.add_team_to_league(club, "Parva Liga", "2025/2026")

        result = leagues_service.generate_schedule("Parva Liga", "2025/2026")
        assert "Недостатъчно" in result

    def test_generate_schedule_with_odd_teams_uses_bye(self):
        _seed_clubs()
        _create_league()
        for club in ("Levski Sofia", "CSKA Sofia", "Ludogorets", "Botev Plovdiv", "Cherno More"):
            leagues_service.add_team_to_league(club, "Parva Liga", "2025/2026")

        result = leagues_service.generate_schedule("Parva Liga", "2025/2026")
        assert "Кръгове: 5" in result
        assert "Мачове: 10" in result

        league = leagues_service.find_league("Parva Liga", "2025/2026")
        rows = db.fetch_all(
            "SELECT round_no, home_club_id, away_club_id FROM matches WHERE league_id = ? ORDER BY round_no, id",
            (league["id"],),
        )
        rounds = {}
        for row in rows:
            rounds.setdefault(row["round_no"], set()).update({row["home_club_id"], row["away_club_id"]})
        assert len(rounds) == 5
        assert all(len(team_ids) == 4 for team_ids in rounds.values())

    def test_generate_schedule_cannot_run_twice(self):
        _seed_clubs()
        _create_league()
        for club in ("Levski Sofia", "CSKA Sofia", "Ludogorets", "Botev Plovdiv"):
            leagues_service.add_team_to_league(club, "Parva Liga", "2025/2026")
        leagues_service.generate_schedule("Parva Liga", "2025/2026")

        result = leagues_service.generate_schedule("Parva Liga", "2025/2026")
        assert "вече" in result.lower()
