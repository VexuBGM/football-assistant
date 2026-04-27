from src import clubs_service, db, leagues_service, matches_service, players_service


def _seed_stage6_data():
    clubs_service.add_club("Levski Sofia", "Sofia", 1914)
    clubs_service.add_club("CSKA Sofia", "Sofia", 1948)
    clubs_service.add_club("Ludogorets", "Razgrad", 2001)
    clubs_service.add_club("Botev Plovdiv", "Plovdiv", 1912)

    players_service.add_player("Ivan Petrov", "Levski Sofia", "MF", 8, "1999-09-09", "Bulgarian")
    players_service.add_player("Petar Dimitrov", "CSKA Sofia", "DF", 5, "1998-06-11", "Bulgarian")
    players_service.add_player("Martin Georgiev", "Ludogorets", "FW", 9, "2000-03-03", "Bulgarian")
    players_service.add_player("Nikolay Kolev", "Botev Plovdiv", "GK", 1, "1997-01-20", "Bulgarian")

    leagues_service.create_league("Parva Liga", "2025/2026")
    for club_name in ("Levski Sofia", "CSKA Sofia", "Ludogorets", "Botev Plovdiv"):
        leagues_service.add_team_to_league(club_name, "Parva Liga", "2025/2026")

    leagues_service.generate_schedule("Parva Liga", "2025/2026")
    league = leagues_service.find_league("Parva Liga", "2025/2026")
    return league


def _first_match():
    return db.fetch_one(
        """
        SELECT
          m.id,
          m.home_club_id,
          m.away_club_id,
          home.name AS home_name,
          away.name AS away_name
        FROM matches m
        JOIN clubs home ON home.id = m.home_club_id
        JOIN clubs away ON away.id = m.away_club_id
        ORDER BY m.round_no ASC, m.id ASC
        """
    )


def _player_for_club(club_name: str):
    return db.fetch_one(
        """
        SELECT p.full_name
        FROM players p
        JOIN clubs c ON c.id = p.club_id
        WHERE c.name = ?
        ORDER BY p.id ASC
        """,
        (club_name,),
    )


class TestMatchesService:
    def test_show_round_lists_matches(self):
        _seed_stage6_data()

        result = matches_service.show_round("Parva Liga", "2025/2026", 1)

        assert 'Кръг 1' in result
        assert "match #" in result
        assert "status scheduled" in result

    def test_record_result_updates_status_and_score(self):
        _seed_stage6_data()
        match_row = _first_match()

        result = matches_service.record_result(
            "Parva Liga",
            "2025/2026",
            match_row["home_name"],
            match_row["away_name"],
            2,
            1,
        )

        assert "Saved result" in result

        updated = db.fetch_one(
            "SELECT home_goals, away_goals, status FROM matches WHERE id = ?",
            (match_row["id"],),
        )
        assert updated["home_goals"] == 2
        assert updated["away_goals"] == 1
        assert updated["status"] == "played"

    def test_record_result_rejects_already_played_match(self):
        _seed_stage6_data()
        match_row = _first_match()
        matches_service.record_result("Parva Liga", "2025/2026", match_row["home_name"], match_row["away_name"], 1, 0)

        result = matches_service.record_result(
            "Parva Liga",
            "2025/2026",
            match_row["home_name"],
            match_row["away_name"],
            3,
            2,
        )

        assert "already has a saved result" in result

    def test_add_goal_rejects_wrong_team_player(self):
        _seed_stage6_data()
        match_row = _first_match()
        outsider_club = next(
            club_name
            for club_name in ("Levski Sofia", "CSKA Sofia", "Ludogorets", "Botev Plovdiv")
            if club_name not in {match_row["home_name"], match_row["away_name"]}
        )

        player = _player_for_club(outsider_club)
        result = matches_service.add_goal_from_text(match_row["id"], f'{player["full_name"]} {outsider_club}', 23)

        assert "does not participate" in result or "not from one of the teams" in result

    def test_add_goal_rejects_invalid_minute(self):
        _seed_stage6_data()
        match_row = _first_match()
        player = _player_for_club(match_row["home_name"])

        result = matches_service.add_goal_from_text(match_row["id"], f'{player["full_name"]} {match_row["home_name"]}', 0)

        assert "between 1 and 120" in result

    def test_add_card_rejects_second_red_card(self):
        _seed_stage6_data()
        match_row = _first_match()
        player = _player_for_club(match_row["home_name"])
        subject = f'{player["full_name"]} {match_row["home_name"]}'

        first = matches_service.add_card_from_text(match_row["id"], subject, "R", 50)
        second = matches_service.add_card_from_text(match_row["id"], subject, "R", 70)

        assert "Card added" in first
        assert "already has a red card" in second

    def test_show_events_returns_chronological_feed(self):
        _seed_stage6_data()
        match_row = _first_match()
        home_player = _player_for_club(match_row["home_name"])
        away_player = _player_for_club(match_row["away_name"])

        matches_service.add_goal_from_text(match_row["id"], f'{home_player["full_name"]} {match_row["home_name"]}', 12)
        matches_service.add_card_from_text(match_row["id"], f'{away_player["full_name"]} {match_row["away_name"]}', "Y", 33)

        result = matches_service.show_events(match_row["id"])

        assert "Events for match" in result
        assert "12' GOAL" in result
        assert "33' CARD Y" in result
