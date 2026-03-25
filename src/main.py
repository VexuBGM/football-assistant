from .chatbot import Chatbot
from .database.db import init_db
from .utils.logger import log_command


def main() -> None:
    init_db()
    bot = Chatbot()

    print("Football Chatbot (Stage 4 - Clubs, Players, Transfers)")
    print('Type "help" for commands.')

    while True:
        user_text = input("> ").strip()
        parsed = bot.parse(user_text)
        result = bot.handle(parsed)

        if result == "EXIT":
            farewell = "Goodbye!"
            log_command(user_text, parsed.intent, parsed.entities, farewell)
            print(farewell)
            break

        log_command(user_text, parsed.intent, parsed.entities, result)
        print(result)


if __name__ == "__main__":
    main()
