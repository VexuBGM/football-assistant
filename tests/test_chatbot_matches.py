from src.chatbot import Chatbot


def _bot():
    return Chatbot()


def _seed_stage6_flow(bot: Chatbot) -> None:
    bot.handle(bot.parse("add club Levski Sofia 1914"))
    bot.handle(bot.parse("add club CSKA Sofia 1948"))
    bot.handle(bot.parse("add club Ludogorets Razgrad 2001"))
    bot.handle(bot.parse("add club Botev Plovdiv 1912"))

    bot.handle(bot.parse("add player Ivan Petrov in Levski position MF number 8 born 1999-09-09 nat Bulgarian"))
    bot.handle(bot.parse("add player Petar Dimitrov in CSKA position DF number 5 born 1998-06-11 nat Bulgarian"))
    bot.handle(bot.parse("add player Martin Georgiev in Ludogorets position FW number 9 born 2000-03-03 nat Bulgarian"))
    bot.handle(bot.parse("add player Nikolay Kolev in Botev position GK number 1 born 1997-01-20 nat Bulgarian"))

    bot.handle(bot.parse("create league Parva Liga 2025/2026"))
    bot.handle(bot.parse("add team Levski to league Parva Liga 2025/2026"))
    bot.handle(bot.parse("add team CSKA to league Parva Liga 2025/2026"))
    bot.handle(bot.parse("add team Ludogorets to league Parva Liga 2025/2026"))
    bot.handle(bot.parse("add team Botev to league Parva Liga 2025/2026"))
    bot.handle(bot.parse("generate schedule Parva Liga 2025/2026"))


class TestParseStage6:
    def test_parse_select_league(self):
        parsed = _bot().parse("select league Parva Liga 2025/2026")
        assert parsed.intent == "select_league"
        assert parsed.entities["league"] == "Parva Liga"

    def test_parse_show_round(self):
        parsed = _bot().parse("show round 1 Parva Liga 2025/2026")
        assert parsed.intent == "show_round"
        assert parsed.entities["round_no"] == 1

    def test_parse_result(self):
        parsed = _bot().parse("result Levski-CSKA 2:1 save")
        assert parsed.intent == "record_result"
        assert parsed.entities["home_team"] == "Levski"
        assert parsed.entities["away_team"] == "CSKA"

    def test_parse_goal_and_card(self):
        goal = _bot().parse("goal Ivan Petrov Levski 23")
        card = _bot().parse("card Ivan Petrov Levski Y 55")

        assert goal.intent == "add_goal"
        assert goal.entities["subject"] == "Ivan Petrov Levski"
        assert card.intent == "add_card"
        assert card.entities["card_type"] == "Y"


class TestHandleStage6:
    def test_help_includes_matches_section(self):
        bot = _bot()
        result = bot.handle(bot.parse("help"))
        assert "Matches" in result
        assert "show round" in result

    def test_result_requires_selected_league(self):
        bot = _bot()
        result = bot.handle(bot.parse("result Levski-CSKA 2:1 save"))
        assert "Select a league first" in result

    def test_goal_requires_selected_match(self):
        bot = _bot()
        result = bot.handle(bot.parse("goal Ivan Petrov Levski 23"))
        assert "Select a match first" in result

    def test_stage6_happy_path(self):
        bot = _bot()
        _seed_stage6_flow(bot)

        round_result = bot.handle(bot.parse("show round 1 Parva Liga 2025/2026"))
        select_league = bot.handle(bot.parse("select league Parva Liga 2025/2026"))

        first_match_line = next(line for line in round_result.splitlines() if "match #" in line)
        match_id = int(first_match_line.split("match #", 1)[1].split(":", 1)[0])
        matchup = first_match_line.split(": ", 1)[1].split(" | ", 1)[0]
        home_team, away_team = matchup.split(" vs ")
        players_by_club = {
            "Levski": "Ivan Petrov",
            "CSKA": "Petar Dimitrov",
            "Ludogorets": "Martin Georgiev",
            "Botev": "Nikolay Kolev",
        }

        select_match = bot.handle(bot.parse(f"select match {match_id}"))
        result_save = bot.handle(bot.parse(f"result {home_team}-{away_team} 2:1 save"))
        goal_add = bot.handle(bot.parse(f'goal {players_by_club[home_team]} {home_team} 23'))
        card_add = bot.handle(bot.parse(f'card {players_by_club[away_team]} {away_team} Y 55'))
        events = bot.handle(bot.parse("show events"))

        assert "Selected league" in select_league
        assert "Selected match" in select_match
        assert "Saved result" in result_save
        assert "Goal added" in goal_add
        assert "Card added" in card_add
        assert "Events for match" in events
