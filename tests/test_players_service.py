# tests/test_players_service.py
from src import clubs_service, players_service


def _add_club(name="Levski", city="Sofia", year=1914):
    clubs_service.add_club(name, city, year)


def _add_player(name="Georgi Petkov", club="Levski", pos="GK", num=1,
                born="1975-05-10", nat="Bulgarian"):
    return players_service.add_player(name, club, pos, num, born, nat)


class TestAddPlayer:
    def test_add_success(self):
        _add_club()
        result = _add_player()
        assert "Georgi Petkov" in result
        assert "GK" in result
        assert "#1" in result
        assert "Levski" in result

    def test_add_empty_name(self):
        _add_club()
        result = players_service.add_player("", "Levski", "GK", 1, "1990-01-01", "Bg")
        assert "empty" in result.lower() or "Error" in result

    def test_add_nonexistent_club(self):
        result = players_service.add_player("Test", "NoClub", "GK", 1, "1990-01-01", "Bg")
        assert "No club" in result or "Add it first" in result

    def test_add_invalid_position(self):
        _add_club()
        result = players_service.add_player("Test", "Levski", "XX", 1, "1990-01-01", "Bg")
        assert "Invalid position" in result
        assert "GK" in result

    def test_add_number_zero(self):
        _add_club()
        result = players_service.add_player("Test", "Levski", "GK", 0, "1990-01-01", "Bg")
        assert "between 1 and 99" in result

    def test_add_number_100(self):
        _add_club()
        result = players_service.add_player("Test", "Levski", "GK", 100, "1990-01-01", "Bg")
        assert "between 1 and 99" in result

    def test_add_number_boundary_1(self):
        _add_club()
        result = _add_player(num=1)
        assert "#1" in result

    def test_add_number_boundary_99(self):
        _add_club()
        result = _add_player(num=99)
        assert "#99" in result

    def test_add_invalid_birth_date(self):
        _add_club()
        result = players_service.add_player("Test", "Levski", "GK", 1, "not-a-date", "Bg")
        assert "Invalid birth date" in result

    def test_add_birth_date_format_dot(self):
        _add_club()
        result = players_service.add_player("Test", "Levski", "GK", 1, "10.05.1975", "Bg")
        assert "1975-05-10" in result

    def test_add_birth_date_format_slash(self):
        _add_club()
        result = players_service.add_player("Test", "Levski", "GK", 1, "10/05/1975", "Bg")
        assert "1975-05-10" in result

    def test_add_birth_date_format_iso(self):
        _add_club()
        result = players_service.add_player("Test", "Levski", "GK", 1, "1975-05-10", "Bg")
        assert "1975-05-10" in result

    def test_add_empty_nationality(self):
        _add_club()
        result = players_service.add_player("Test", "Levski", "GK", 1, "1990-01-01", "")
        assert "empty" in result.lower() or "Error" in result

    def test_add_duplicate_number_in_club(self):
        _add_club()
        _add_player(name="Player1", num=1)
        result = _add_player(name="Player2", num=1)
        assert "already taken" in result

    def test_add_same_number_different_clubs(self):
        _add_club("Levski", "Sofia")
        _add_club("CSKA", "Sofia")
        _add_player(name="Player1", club="Levski", num=1)
        result = _add_player(name="Player2", club="CSKA", num=1)
        assert "Player2" in result  # should succeed

    def test_add_club_by_id(self):
        _add_club()
        result = players_service.add_player("Test", "1", "GK", 5, "1990-01-01", "Bg")
        assert "Test" in result
        assert "Levski" in result

    def test_add_position_case_insensitive(self):
        _add_club()
        result = _add_player(pos="gk")
        assert "GK" in result

    def test_add_all_positions(self):
        _add_club()
        for i, pos in enumerate(["GK", "DF", "MF", "FW"], start=1):
            result = players_service.add_player(f"Player{i}", "Levski", pos, i, "1990-01-01", "Bg")
            assert pos in result


class TestListPlayers:
    def test_no_players(self):
        _add_club()
        result = players_service.list_players()
        assert "No players" in result

    def test_no_players_in_club(self):
        _add_club()
        result = players_service.list_players("Levski")
        assert "No players" in result

    def test_list_all(self):
        _add_club("Levski", "Sofia")
        _add_club("CSKA", "Sofia")
        _add_player(name="Player1", club="Levski", num=1)
        _add_player(name="Player2", club="CSKA", num=9)
        result = players_service.list_players()
        assert "Player1" in result
        assert "Player2" in result
        assert "All players" in result

    def test_list_by_club(self):
        _add_club("Levski", "Sofia")
        _add_club("CSKA", "Sofia")
        _add_player(name="Player1", club="Levski", num=1)
        _add_player(name="Player2", club="CSKA", num=9)
        result = players_service.list_players("Levski")
        assert "Player1" in result
        assert "Player2" not in result

    def test_list_nonexistent_club(self):
        result = players_service.list_players("NoClub")
        assert "No club" in result

    def test_list_shows_injured_status(self):
        _add_club()
        _add_player()
        players_service.update_player("Georgi Petkov", status="injured")
        result = players_service.list_players()
        assert "[injured]" in result

    def test_list_active_no_status_tag(self):
        _add_club()
        _add_player()
        result = players_service.list_players()
        assert "[active]" not in result

    def test_list_ordered_by_number(self):
        _add_club()
        _add_player(name="Player10", num=10)
        _add_player(name="Player2", num=2)
        result = players_service.list_players("Levski")
        p2_pos = result.index("Player2")
        p10_pos = result.index("Player10")
        assert p2_pos < p10_pos


class TestUpdatePlayer:
    def test_update_number(self):
        _add_club()
        _add_player()
        result = players_service.update_player("Georgi Petkov", number=13)
        assert "number -> #13" in result

    def test_update_position(self):
        _add_club()
        _add_player()
        result = players_service.update_player("Georgi Petkov", position="DF")
        assert "position -> DF" in result

    def test_update_status(self):
        _add_club()
        _add_player()
        result = players_service.update_player("Georgi Petkov", status="injured")
        assert "status -> injured" in result

    def test_update_multiple_fields(self):
        _add_club()
        _add_player()
        result = players_service.update_player("Georgi Petkov", number=13, position="DF")
        assert "position -> DF" in result
        assert "number -> #13" in result

    def test_update_no_changes(self):
        _add_club()
        _add_player(pos="GK", num=1)
        result = players_service.update_player("Georgi Petkov", position="GK", number=1)
        assert "No changes" in result

    def test_update_nonexistent_player(self):
        result = players_service.update_player("Nobody")
        assert "No player" in result

    def test_update_empty_name(self):
        result = players_service.update_player("")
        assert "Error" in result or "must specify" in result

    def test_update_invalid_position(self):
        _add_club()
        _add_player()
        result = players_service.update_player("Georgi Petkov", position="XX")
        assert "Invalid position" in result

    def test_update_invalid_number_zero(self):
        _add_club()
        _add_player()
        result = players_service.update_player("Georgi Petkov", number=0)
        assert "between 1 and 99" in result

    def test_update_invalid_number_100(self):
        _add_club()
        _add_player()
        result = players_service.update_player("Georgi Petkov", number=100)
        assert "between 1 and 99" in result

    def test_update_duplicate_number(self):
        _add_club()
        _add_player(name="Player1", num=1)
        _add_player(name="Player2", num=2)
        result = players_service.update_player("Player2", number=1)
        assert "already taken" in result

    def test_update_invalid_status(self):
        _add_club()
        _add_player()
        result = players_service.update_player("Georgi Petkov", status="bogus")
        assert "Invalid status" in result

    def test_update_all_valid_statuses(self):
        _add_club()
        _add_player()
        for s in ["injured", "suspended", "retired", "active"]:
            result = players_service.update_player("Georgi Petkov", status=s)
            # First three will show change, last one may show "No changes" if already active
            assert "Updated" in result or "No changes" in result

    def test_update_same_number_own_player(self):
        _add_club()
        _add_player(num=1)
        result = players_service.update_player("Georgi Petkov", number=1)
        assert "No changes" in result


class TestDeletePlayer:
    def test_delete_by_name(self):
        _add_club()
        _add_player()
        result = players_service.delete_player("Georgi Petkov")
        assert "Deleted" in result
        assert "Georgi Petkov" in result

    def test_delete_by_id(self):
        _add_club()
        _add_player()
        result = players_service.delete_player("1")
        assert "Deleted" in result

    def test_delete_nonexistent_name(self):
        result = players_service.delete_player("Nobody")
        assert "No player" in result

    def test_delete_nonexistent_id(self):
        result = players_service.delete_player("999")
        assert "No player" in result

    def test_delete_empty(self):
        result = players_service.delete_player("")
        assert "Error" in result or "must specify" in result

    def test_delete_removes_from_list(self):
        _add_club()
        _add_player()
        players_service.delete_player("Georgi Petkov")
        result = players_service.list_players()
        assert "Georgi Petkov" not in result

    def test_delete_case_insensitive(self):
        _add_club()
        _add_player()
        result = players_service.delete_player("georgi petkov")
        assert "Deleted" in result


class TestSeedTestData:
    def test_seed_no_clubs_adds_nothing(self):
        result = players_service.seed_test_data()
        assert "0" in result or "Loaded 0" in result

    def test_seed_with_clubs(self):
        _add_club("Levski Sofia", "Sofia")
        _add_club("CSKA Sofia", "Sofia")
        _add_club("Ludogorets", "Razgrad")
        result = players_service.seed_test_data()
        assert "Loaded 8" in result

    def test_seed_idempotent(self):
        _add_club("Levski Sofia", "Sofia")
        _add_club("CSKA Sofia", "Sofia")
        _add_club("Ludogorets", "Razgrad")
        players_service.seed_test_data()
        result = players_service.seed_test_data()
        assert "already loaded" in result.lower()
