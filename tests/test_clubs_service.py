# tests/test_clubs_service.py
from src import clubs_service


class TestAddClub:
    def test_add_club_success(self):
        result = clubs_service.add_club("Levski", "Sofia", 1914)
        assert "Levski" in result
        assert "Sofia" in result

    def test_add_club_without_year(self):
        result = clubs_service.add_club("Levski", "Sofia")
        assert "Levski" in result

    def test_add_club_duplicate(self):
        clubs_service.add_club("Levski", "Sofia", 1914)
        result = clubs_service.add_club("Levski", "Sofia", 1914)
        assert "already exists" in result

    def test_add_club_duplicate_case_insensitive(self):
        clubs_service.add_club("Levski", "Sofia")
        result = clubs_service.add_club("LEVSKI", "Sofia")
        assert "already exists" in result

    def test_add_club_empty_name(self):
        result = clubs_service.add_club("", "Sofia")
        assert "празно" in result or "empty" in result.lower()

    def test_add_club_empty_city(self):
        result = clubs_service.add_club("Levski", "")
        assert "празен" in result or "empty" in result.lower()

    def test_add_club_whitespace_normalized(self):
        result = clubs_service.add_club("  Levski  ", "  Sofia  ")
        assert "Levski" in result
        assert "Sofia" in result


class TestGetAllClubs:
    def test_no_clubs(self):
        result = clubs_service.get_all_clubs()
        assert "Няма" in result or "No" in result

    def test_list_clubs(self):
        clubs_service.add_club("Levski", "Sofia", 1914)
        clubs_service.add_club("CSKA", "Sofia", 1948)
        result = clubs_service.get_all_clubs()
        assert "Levski" in result
        assert "CSKA" in result
        assert "1914" in result

    def test_clubs_sorted_by_name(self):
        clubs_service.add_club("Levski", "Sofia")
        clubs_service.add_club("CSKA", "Sofia")
        result = clubs_service.get_all_clubs()
        cska_pos = result.index("CSKA")
        levski_pos = result.index("Levski")
        assert cska_pos < levski_pos


class TestDeleteClub:
    def test_delete_by_id(self):
        clubs_service.add_club("Levski", "Sofia", 1914)
        result = clubs_service.delete_club("1")
        assert "Levski" in result

    def test_delete_by_name(self):
        clubs_service.add_club("Levski", "Sofia")
        result = clubs_service.delete_club("Levski")
        assert "Levski" in result

    def test_delete_nonexistent_id(self):
        result = clubs_service.delete_club("999")
        assert "999" in result

    def test_delete_nonexistent_name(self):
        result = clubs_service.delete_club("Nonexistent")
        assert "Nonexistent" in result

    def test_delete_empty_identifier(self):
        result = clubs_service.delete_club("")
        assert "ID" in result or "име" in result

    def test_delete_removes_from_list(self):
        clubs_service.add_club("Levski", "Sofia")
        clubs_service.delete_club("Levski")
        result = clubs_service.get_all_clubs()
        assert "Levski" not in result


class TestUpdateClub:
    def test_update_name(self):
        clubs_service.add_club("Levski", "Sofia", 1914)
        result = clubs_service.update_club(1, name="Levski Sofia")
        assert "Levski Sofia" in result

    def test_update_city(self):
        clubs_service.add_club("Levski", "Sofia")
        result = clubs_service.update_club(1, city="Plovdiv")
        assert "Plovdiv" in result

    def test_update_founded_year(self):
        clubs_service.add_club("Levski", "Sofia")
        result = clubs_service.update_club(1, founded_year=1914)
        assert "Levski" in result

    def test_update_nonexistent(self):
        result = clubs_service.update_club(999, name="Test")
        assert "999" in result

    def test_update_duplicate_name(self):
        clubs_service.add_club("Levski", "Sofia")
        clubs_service.add_club("CSKA", "Sofia")
        result = clubs_service.update_club(2, name="Levski")
        assert "already exists" in result or "вече" in result.lower()

    def test_update_empty_name(self):
        clubs_service.add_club("Levski", "Sofia")
        result = clubs_service.update_club(1, name="")
        assert "празно" in result or "empty" in result.lower()

    def test_update_empty_city(self):
        clubs_service.add_club("Levski", "Sofia")
        result = clubs_service.update_club(1, city="")
        assert "празен" in result or "empty" in result.lower()
