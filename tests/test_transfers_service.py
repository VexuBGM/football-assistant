from src import clubs_service, db, players_service, transfers_service


def _seed_base_data():
    clubs_service.add_club("Levski", "Sofia", 1914)
    clubs_service.add_club("CSKA", "Sofia", 1948)
    clubs_service.add_club("Ludogorets", "Razgrad", 2001)
    clubs_service.add_club("Botev", "Plovdiv", 1912)
    players_service.add_player("Ivan Petrov", "Levski", "MF", 8, "1999-09-09", "Bulgarian")
    players_service.add_player("Petar Kolev", "CSKA", "DF", 5, "1998-06-11", "Bulgarian")


class TestTransferPlayer:
    def test_valid_transfer_success(self):
        _seed_base_data()

        result = transfers_service.transfer_player(
            "Ivan Petrov",
            "Levski",
            "Ludogorets",
            "2026-03-10",
            50000,
        )

        assert "Transfer completed" in result
        assert "Ivan Petrov" in result
        assert "Levski" in result
        assert "Ludogorets" in result
        assert "2026-03-10" in result

        player = players_service.find_player("Ivan Petrov")
        assert player is not None
        assert player["club_name"] == "Ludogorets"

        count = db.fetch_one("SELECT COUNT(*) AS count FROM transfers WHERE player_id = ?", (player["id"],))
        assert count["count"] == 1

    def test_transfer_wrong_source_club_refused(self):
        _seed_base_data()

        result = transfers_service.transfer_player(
            "Ivan Petrov",
            "CSKA",
            "Ludogorets",
            "2026-03-10",
        )

        assert "currently belongs to Levski" in result

        player = players_service.find_player("Ivan Petrov")
        assert player["club_name"] == "Levski"
        count = db.fetch_one("SELECT COUNT(*) AS count FROM transfers")
        assert count["count"] == 0

    def test_transfer_to_missing_club_refused(self):
        _seed_base_data()

        result = transfers_service.transfer_player(
            "Ivan Petrov",
            "Levski",
            "NoClub",
            "2026-03-10",
        )

        assert "No club found" in result
        assert "NoClub" in result

    def test_transfer_same_source_and_destination_refused(self):
        _seed_base_data()

        result = transfers_service.transfer_player(
            "Ivan Petrov",
            "Levski",
            "Levski",
            "2026-03-10",
        )

        assert "source and destination clubs must be different" in result

    def test_free_agent_transfer_is_allowed_only_with_free_agent_source(self):
        _seed_base_data()
        db.execute("UPDATE players SET club_id = NULL WHERE lower(full_name) = lower(?)", ("Ivan Petrov",))

        denied = transfers_service.transfer_player(
            "Ivan Petrov",
            "Levski",
            "Botev",
            "2026-03-10",
        )
        assert "currently without a club" in denied

        result = transfers_service.transfer_player(
            "Ivan Petrov",
            "free agent",
            "Botev",
            "2026-03-10",
        )
        assert "Transfer completed" in result
        assert "Free agent" in result


class TestTransferHistory:
    def test_list_transfers_by_player(self):
        _seed_base_data()
        transfers_service.transfer_player("Ivan Petrov", "Levski", "Ludogorets", "2025-01-10", 50000)
        transfers_service.transfer_player("Ivan Petrov", "Ludogorets", "CSKA", "2025-08-01", 75000)

        result = transfers_service.list_transfers_by_player("Ivan Petrov")

        assert "Transfers for Ivan Petrov" in result
        assert "2025-01-10" in result
        assert "2025-08-01" in result
        assert "Levski -> Ludogorets" in result
        assert "Ludogorets -> CSKA" in result

    def test_list_transfers_by_club(self):
        _seed_base_data()
        transfers_service.transfer_player("Ivan Petrov", "Levski", "Ludogorets", "2025-01-10", 50000)

        result = transfers_service.list_transfers_by_club("Ludogorets")

        assert "Transfers for club Ludogorets" in result
        assert "[IN]" in result
        assert "Ivan Petrov" in result


class TestTransferSeedHistory:
    def test_seed_transfer_history_loads_minimum_demo_data(self):
        result = transfers_service.seed_transfer_history()

        assert "Loaded 5" in result

        clubs_count = db.fetch_one("SELECT COUNT(*) AS count FROM clubs")
        players_count = db.fetch_one("SELECT COUNT(*) AS count FROM players")
        transfers_count = db.fetch_one("SELECT COUNT(*) AS count FROM transfers")

        assert clubs_count["count"] >= 4
        assert players_count["count"] >= 6
        assert transfers_count["count"] >= 5
