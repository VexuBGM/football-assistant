import os
import tempfile
from pathlib import Path

from src import db
from src.chatbot import Chatbot
from src.utils.logger import log_command


ROOT = Path(__file__).resolve().parent
LOG_PATH = ROOT / "commands.log"
TEMP_DB_DIR = ROOT / ".test_dbs"


def main() -> None:
    original_log = LOG_PATH.read_text(encoding="utf-8") if LOG_PATH.exists() else ""
    TEMP_DB_DIR.mkdir(exist_ok=True)
    fd, db_path = tempfile.mkstemp(prefix="manual_all_stages_", suffix=".db", dir=TEMP_DB_DIR)
    os.close(fd)

    db._DB_CONN = None
    db.get_db_path = lambda: db_path
    db.init_db()
    bot = Chatbot()
    checks: list[str] = []

    def run(command: str, expected: str | list[str]) -> str:
        parsed = bot.parse(command)
        result = bot.handle(parsed)
        log_command(command, parsed.intent, parsed.entities, result)
        expected_values = [expected] if isinstance(expected, str) else expected
        missing = [value for value in expected_values if value not in result]
        if missing:
            raise AssertionError(
                f"Command failed expectation: {command}\n"
                f"Missing: {missing}\n"
                f"Actual result:\n{result}"
            )
        checks.append(f"OK | {command} -> {result.splitlines()[0]}")
        return result

    try:
        run("help", ["Commands:", "AI Prediction"])

        for club in ("Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"):
            run(f"add club {club} City 2000", f"Added club: {club}")
        run("add club Temp Town 1999", "Added club: Temp")
        run("delete club Temp", "Deleted club: Temp.")
        run("add club Alpha City 2000", 'Club with name "Alpha" already exists.')
        run("list clubs", ["Alpha", "Zeta"])

        run("add player Ivan Alpha in Alpha position MF number 8 born 1999-09-09 nat Bulgarian", "Added player: Ivan Alpha")
        run("add player Peter Beta in Beta position DF number 5 born 1998-06-11 nat Bulgarian", "Added player: Peter Beta")
        run("add player Spare Gamma in Gamma position FW number 11 born 2000-01-02 nat Bulgarian", "Added player: Spare Gamma")
        run("add player Bad Guy in Alpha position XX number 77 born 2000-01-01 nat Bulgarian", "Invalid position")
        run("list players of Alpha", "Ivan Alpha")
        run("change number of Ivan Alpha to 10", "Updated Ivan Alpha")
        run("change status of Spare Gamma to injured", "Updated Spare Gamma")
        run("delete player Spare Gamma", "Deleted player: Spare Gamma.")

        run("create league Parva Liga 2025/2026", "Created league")
        run("create league Parva Liga 2025/2026", "already exists")
        for club in ("Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"):
            run(f"add team {club} to league Parva Liga 2025/2026", f'"{club}"')
        run("add team Alpha to league Parva Liga 2025/2026", "вече")
        run("show teams in league Parva Liga 2025/2026", ["Alpha", "Zeta"])
        run("generate schedule Parva Liga 2025/2026", ["Кръгове: 5", "Мачове: 15"])
        run("generate schedule Parva Liga 2025/2026", "вече")
        run("select league Parva Liga 2025/2026", "Selected league")
        run("show round 1 Parva Liga 2025/2026", "match #")

        league = db.fetch_one(
            "SELECT id FROM leagues WHERE name = ? AND season = ?",
            ("Parva Liga", "2025/2026"),
        )
        match_rows = db.fetch_all(
            """
            SELECT m.id, home.name AS home_name, away.name AS away_name
            FROM matches m
            JOIN clubs home ON home.id = m.home_club_id
            JOIN clubs away ON away.id = m.away_club_id
            WHERE m.league_id = ?
            ORDER BY m.id ASC
            """,
            (league["id"],),
        )
        score_cycle = [(2, 1), (1, 1), (0, 2), (3, 0), (2, 2)]
        alpha_beta_match_id = None
        for index, row in enumerate(match_rows):
            home = row["home_name"]
            away = row["away_name"]
            home_goals, away_goals = score_cycle[index % len(score_cycle)]
            run(f"result {home}-{away} {home_goals}:{away_goals} save", "Saved result")
            if {home, away} == {"Alpha", "Beta"}:
                alpha_beta_match_id = int(row["id"])

        assert alpha_beta_match_id is not None
        run(f"select match {alpha_beta_match_id}", "Selected match")
        run("goal Ivan Alpha Alpha 23", "Goal added")
        run("card Peter Beta Beta Y 55", "Card added")
        run("goal Ivan Alpha Alpha 0", "Minute must be between 1 and 120.")
        run("show events", ["GOAL", "CARD"])

        run("show standings Parva Liga 2025/2026", ["Класиране", "PTS"])
        prediction = run("prediction Alpha vs Beta", ["Победа Alpha:", "Равен:", "Победа Beta:"])
        percentages = [
            int(line.rsplit(":", 1)[1].strip().rstrip("%"))
            for line in prediction.splitlines()
            if line.startswith("Победа ") or line.startswith("Равен:")
        ]
        if sum(percentages) != 100:
            raise AssertionError(f"Prediction percentages do not sum to 100: {percentages}")

        run("prediction Alpha vs Missing", 'Отборът "Missing" не съществува.')
        run("transfer Ivan Alpha from Alpha to Beta 2026-03-10 fee 1000", "Transfer completed")
        run("show transfers of Ivan Alpha", "Alpha -> Beta")
        run("transfer Ivan Alpha from Alpha to Gamma 2026-03-11", "currently belongs to Beta")
        run("transfer Peter Beta from Beta to Beta 2026-03-10", "source and destination clubs must be different")
        run("show transfers of club Beta", "Transfers for club Beta")

        appended_log = LOG_PATH.read_text(encoding="utf-8")[len(original_log):]
        if "INPUT: prediction Alpha vs Beta" not in appended_log:
            raise AssertionError("Manual logging check failed: prediction command was not logged.")
        if "RESULT: OK" not in appended_log or "RESULT: ERROR" not in appended_log:
            raise AssertionError("Manual logging check failed: expected OK and ERROR statuses.")

        print(f"MANUAL VERIFICATION PASSED: {len(checks)} chatbot commands checked.")
        for line in checks:
            print(line)
    finally:
        if db._DB_CONN is not None:
            db._DB_CONN.close()
            db._DB_CONN = None
        if os.path.exists(db_path):
            os.remove(db_path)
        LOG_PATH.write_text(original_log, encoding="utf-8")


if __name__ == "__main__":
    main()
