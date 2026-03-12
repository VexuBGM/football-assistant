# src/main.py
from datetime import datetime
import os

from .db import init_db
from .chatbot import Chatbot


def log_command(user_text: str, result: str) -> None:
    # commands.log в корена на проекта
    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "commands.log"))
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] INPUT: {user_text}\n")
        f.write(f"[{ts}] OUTPUT: {result}\n")
        f.write("-" * 40 + "\n")


def main():
    init_db()  # зарежда schema.sql ако трябва
    bot = Chatbot()

    print("⚽ Football Chatbot (Stage 3 — Clubs + Players)")
    print('Type "help" for commands.')

    while True:
        user_text = input("> ").strip()
        parsed = bot.parse(user_text)
        result = bot.handle(parsed)

        if result == "EXIT":
            log_command(user_text, "Довиждане!")
            print("Довиждане!")
            break

        log_command(user_text, result)
        print(result)


if __name__ == "__main__":
    main()
