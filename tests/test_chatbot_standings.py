from src import db
from src.chatbot import Chatbot


def _bot():
    return Chatbot()


def _seed_standings_flow(bot: Chatbot) -> None:
    bot.handle(bot.parse("add club Alpha Sofia 2000"))
    bot.handle(bot.parse("add club Beta Plovdiv 2000"))
    bot.handle(bot.parse("add club Gamma Varna 2000"))
    bot.handle(bot.parse("add club Delta Burgas 2000"))
    bot.handle(bot.parse("create league Parva Liga 2025/2026"))
    for club_name in ("Alpha", "Beta", "Gamma", "Delta"):
        bot.handle(bot.parse(f"add team {club_name} to league Parva Liga 2025/2026"))
    bot.handle(bot.parse("generate schedule Parva Liga 2025/2026"))


class TestParseStage7:
    def test_parse_show_standings_english(self):
        parsed = _bot().parse("show standings Parva Liga 2025/2026")

        assert parsed.intent == "show_standings"
        assert parsed.entities["league"] == "Parva Liga"
        assert parsed.entities["season"] == "2025/2026"

    def test_parse_show_standings_bulgarian(self):
        parsed = _bot().parse("Покажи класиране Първа лига 2025/2026")

        assert parsed.intent == "show_standings"
        assert parsed.entities["league"] == "Първа лига"


class TestHandleStage7:
    def test_help_includes_standings_section(self):
        result = _bot().handle(_bot().parse("help"))

        assert "Standings" in result
        assert "show standings" in result

    def test_show_standings_after_result_entry(self):
        bot = _bot()
        _seed_standings_flow(bot)
        round_result = bot.handle(bot.parse("show round 1 Parva Liga 2025/2026"))
        first_match_line = next(line for line in round_result.splitlines() if "match #" in line)
        matchup = first_match_line.split(": ", 1)[1].split(" | ", 1)[0]
        home_team, away_team = matchup.split(" vs ")

        bot.handle(bot.parse("select league Parva Liga 2025/2026"))
        bot.handle(bot.parse(f"result {home_team}-{away_team} 2:1 save"))
        standings = bot.handle(bot.parse("show standings Parva Liga 2025/2026"))

        assert "Класиране за лига" in standings
        assert f"1. {home_team} 1 1 0 0 2:1 +1 3" in standings
        assert away_team in standings

        played_count = db.fetch_one("SELECT COUNT(*) AS count FROM matches WHERE status = 'played'")
        assert played_count["count"] == 1
