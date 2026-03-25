from src.chatbot import Chatbot


def _bot():
    return Chatbot()


class TestParseTransfers:
    def test_parse_transfer_bg_with_fee(self):
        parsed = _bot().parse("Трансфер Иван Петров от Левски в Лудогорец 2026-03-10 сума 50000")

        assert parsed.intent == "transfer_player"
        assert parsed.entities["player_name"] == "Иван Петров"
        assert parsed.entities["from_club"] == "Левски"
        assert parsed.entities["to_club"] == "Лудогорец"
        assert parsed.entities["date"] == "2026-03-10"
        assert parsed.entities["fee"] == "50000"

    def test_parse_show_transfers_player_bg(self):
        parsed = _bot().parse("Покажи трансфери на Иван Петров")

        assert parsed.intent == "show_transfers_player"
        assert parsed.entities["name"] == "Иван Петров"

    def test_parse_show_transfers_club_bg(self):
        parsed = _bot().parse("Покажи трансфери на Левски")

        assert parsed.intent == "show_transfers_club"
        assert parsed.entities["name"] == "Левски"


class TestHandleTransfers:
    def test_handle_transfer_and_history(self):
        bot = _bot()
        bot.handle(bot.parse("add club Levski Sofia 1914"))
        bot.handle(bot.parse("add club Ludogorets Razgrad 2001"))
        bot.handle(
            bot.parse(
                "add player Ivan Petrov in Levski position MF number 8 born 1999-09-09 nat Bulgarian"
            )
        )

        transfer_result = bot.handle(
            bot.parse("transfer Ivan Petrov from Levski to Ludogorets 2026-03-10 fee 50000")
        )
        history_result = bot.handle(bot.parse("show transfers of Ivan Petrov"))

        assert "Transfer completed" in transfer_result
        assert "Ivan Petrov" in transfer_result
        assert "Ludogorets" in transfer_result
        assert "Transfers for Ivan Petrov" in history_result
        assert "2026-03-10" in history_result
