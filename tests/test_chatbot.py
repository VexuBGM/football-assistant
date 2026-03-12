# tests/test_chatbot.py
from src.chatbot import Chatbot, ParseResult
from src import clubs_service, players_service


def _bot():
    return Chatbot()


# ─── Parse tests ───


class TestParseHelp:
    def test_help_en(self):
        assert _bot().parse("help").intent == "help"

    def test_help_bg(self):
        assert _bot().parse("помощ").intent == "help"


class TestParseExit:
    def test_exit(self):
        assert _bot().parse("exit").intent == "exit"

    def test_quit(self):
        assert _bot().parse("quit").intent == "exit"

    def test_exit_bg(self):
        assert _bot().parse("изход").intent == "exit"


class TestParseAddClub:
    def test_add_club_en(self):
        p = _bot().parse("add club Levski Sofia 1914")
        assert p.intent == "add_club"
        assert p.entities["name"] == "Levski"
        assert p.entities["city"] == "Sofia"
        assert p.entities["founded_year"] == 1914

    def test_add_club_no_year(self):
        p = _bot().parse("add club Levski Sofia")
        assert p.intent == "add_club"
        assert p.entities["founded_year"] is None


class TestParseDeleteClub:
    def test_delete_club_en(self):
        p = _bot().parse("delete club Levski")
        assert p.intent == "delete_club"
        assert p.entities["identifier"] == "Levski"

    def test_delete_club_by_id(self):
        p = _bot().parse("delete club 1")
        assert p.entities["identifier"] == "1"


class TestParseListClubs:
    def test_list_clubs_en(self):
        assert _bot().parse("list clubs").intent == "list_clubs"

    def test_list_clubs_bg(self):
        assert _bot().parse("покажи всички клубове").intent == "list_clubs"


class TestParseAddPlayer:
    def test_add_player_en(self):
        p = _bot().parse("add player Georgi Petkov in Levski position GK number 1 born 1975-05-10 nat Bulgarian")
        assert p.intent == "add_player"
        assert p.entities["full_name"] == "Georgi Petkov"
        assert p.entities["club"] == "Levski"
        assert p.entities["position"] == "GK"
        assert p.entities["number"] == 1
        assert p.entities["birth_date"] == "1975-05-10"
        assert p.entities["nationality"] == "Bulgarian"

    def test_add_player_bg(self):
        p = _bot().parse("добави играч Иван Иванов в ЦСКА позиция DF номер 5 роден 1990-01-01 нац Българин")
        assert p.intent == "add_player"
        assert p.entities["full_name"] == "Иван Иванов"
        assert p.entities["club"] == "ЦСКА"
        assert p.entities["position"] == "DF"
        assert p.entities["number"] == 5


class TestParseListPlayers:
    def test_list_players_of_club_en(self):
        p = _bot().parse("list players of Levski")
        assert p.intent == "list_players"
        assert p.entities["club"] == "Levski"

    def test_list_all_players_en(self):
        p = _bot().parse("list players")
        assert p.intent == "list_players"
        assert p.entities["club"] is None

    def test_list_players_bg(self):
        p = _bot().parse("покажи играчи на Левски")
        assert p.intent == "list_players"
        assert p.entities["club"] == "Левски"

    def test_list_all_players_bg(self):
        p = _bot().parse("покажи всички играчи")
        assert p.intent == "list_players"

    def test_players_shortcut_bg(self):
        p = _bot().parse("играчи на ЦСКА")
        assert p.intent == "list_players"
        assert p.entities["club"] == "ЦСКА"

    def test_players_all_shortcut_bg(self):
        p = _bot().parse("играчи")
        assert p.intent == "list_players"


class TestParseUpdatePlayer:
    def test_change_number_en(self):
        p = _bot().parse("change number of Georgi Petkov to 13")
        assert p.intent == "update_player_number"
        assert p.entities["player_name"] == "Georgi Petkov"
        assert p.entities["number"] == 13

    def test_change_number_bg(self):
        p = _bot().parse("смени номер на Георги Петков на 13")
        assert p.intent == "update_player_number"
        assert p.entities["player_name"] == "Георги Петков"
        assert p.entities["number"] == 13

    def test_change_position_en(self):
        p = _bot().parse("change position of Yuri Gali to FW")
        assert p.intent == "update_player_position"
        assert p.entities["player_name"] == "Yuri Gali"
        assert p.entities["position"] == "FW"

    def test_change_position_bg(self):
        p = _bot().parse("смени позиция на Юри Гали на FW")
        assert p.intent == "update_player_position"

    def test_change_status_en(self):
        p = _bot().parse("change status of Stefan Velev to injured")
        assert p.intent == "update_player_status"
        assert p.entities["player_name"] == "Stefan Velev"
        assert p.entities["status"] == "injured"

    def test_change_status_bg(self):
        p = _bot().parse("смени статус на Стефан Велев на injured")
        assert p.intent == "update_player_status"


class TestParseDeletePlayer:
    def test_delete_player_en(self):
        p = _bot().parse("delete player Georgi Petkov")
        assert p.intent == "delete_player"
        assert p.entities["identifier"] == "Georgi Petkov"

    def test_delete_player_bg(self):
        p = _bot().parse("изтрий играч Георги Петков")
        assert p.intent == "delete_player"
        assert p.entities["identifier"] == "Георги Петков"


class TestParseSeedPlayers:
    def test_seed_en(self):
        assert _bot().parse("seed players").intent == "seed_players"

    def test_seed_bg(self):
        assert _bot().parse("зареди тестови играчи").intent == "seed_players"


class TestParseUnknown:
    def test_garbage(self):
        assert _bot().parse("xyzzy foo bar").intent == "unknown"

    def test_empty(self):
        assert _bot().parse("").intent == "unknown"


# ─── Handle tests ───


class TestHandleHelp:
    def test_help_returns_commands(self):
        bot = _bot()
        result = bot.handle(bot.parse("help"))
        assert "Clubs" in result
        assert "Players" in result


class TestHandleExit:
    def test_exit_returns_exit_signal(self):
        bot = _bot()
        result = bot.handle(bot.parse("exit"))
        assert result == "EXIT"


class TestHandleUnknown:
    def test_unknown_message(self):
        bot = _bot()
        result = bot.handle(bot.parse("asdfghjkl"))
        assert "help" in result.lower()


class TestHandleClubsCRUD:
    def test_add_and_list(self):
        bot = _bot()
        bot.handle(bot.parse("add club Levski Sofia 1914"))
        result = bot.handle(bot.parse("list clubs"))
        assert "Levski" in result

    def test_delete_club(self):
        bot = _bot()
        bot.handle(bot.parse("add club Levski Sofia 1914"))
        result = bot.handle(bot.parse("delete club Levski"))
        assert "Levski" in result


class TestHandlePlayersCRUD:
    def test_add_player(self):
        bot = _bot()
        bot.handle(bot.parse("add club Levski Sofia 1914"))
        result = bot.handle(bot.parse(
            "add player Georgi Petkov in Levski position GK number 1 born 1975-05-10 nat Bulgarian"
        ))
        assert "Georgi Petkov" in result

    def test_list_players_of_club(self):
        bot = _bot()
        bot.handle(bot.parse("add club Levski Sofia 1914"))
        bot.handle(bot.parse(
            "add player Georgi Petkov in Levski position GK number 1 born 1975-05-10 nat Bulgarian"
        ))
        result = bot.handle(bot.parse("list players of Levski"))
        assert "Georgi Petkov" in result

    def test_change_number(self):
        bot = _bot()
        bot.handle(bot.parse("add club Levski Sofia 1914"))
        bot.handle(bot.parse(
            "add player Georgi Petkov in Levski position GK number 1 born 1975-05-10 nat Bulgarian"
        ))
        result = bot.handle(bot.parse("change number of Georgi Petkov to 13"))
        assert "#13" in result

    def test_change_position(self):
        bot = _bot()
        bot.handle(bot.parse("add club Levski Sofia 1914"))
        bot.handle(bot.parse(
            "add player Georgi Petkov in Levski position GK number 1 born 1975-05-10 nat Bulgarian"
        ))
        result = bot.handle(bot.parse("change position of Georgi Petkov to DF"))
        assert "DF" in result

    def test_change_status(self):
        bot = _bot()
        bot.handle(bot.parse("add club Levski Sofia 1914"))
        bot.handle(bot.parse(
            "add player Georgi Petkov in Levski position GK number 1 born 1975-05-10 nat Bulgarian"
        ))
        result = bot.handle(bot.parse("change status of Georgi Petkov to injured"))
        assert "injured" in result

    def test_delete_player(self):
        bot = _bot()
        bot.handle(bot.parse("add club Levski Sofia 1914"))
        bot.handle(bot.parse(
            "add player Georgi Petkov in Levski position GK number 1 born 1975-05-10 nat Bulgarian"
        ))
        result = bot.handle(bot.parse("delete player Georgi Petkov"))
        assert "Deleted" in result

    def test_seed_players(self):
        bot = _bot()
        bot.handle(bot.parse("add club Levski Sofia Sofia"))
        bot.handle(bot.parse("add club CSKA Sofia Sofia"))
        bot.handle(bot.parse("add club Ludogorets Razgrad"))
        result = bot.handle(bot.parse("seed players"))
        assert "Loaded" in result or "already" in result.lower()
