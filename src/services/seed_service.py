from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..database.db import fetch_one, transaction


DEMO_LEAGUE = "Seeded Premier League"
DEMO_SEASON = "2025/2026"
SANDBOX_LEAGUE = "Seeded Match Sandbox"
SANDBOX_SEASON = "2026/2027"


@dataclass(frozen=True)
class PlayerSeed:
    name: str
    club: str
    birth_date: str
    nationality: str
    position: str
    number: int
    status: str = "active"


CLUBS = [
    ("Levski Sofia", "Sofia", 1914),
    ("CSKA Sofia", "Sofia", 1948),
    ("Ludogorets", "Razgrad", 2001),
    ("Botev Plovdiv", "Plovdiv", 1912),
    ("Cherno More", "Varna", 1913),
    ("Lokomotiv Plovdiv", "Plovdiv", 1926),
]

PLAYERS = [
    PlayerSeed("Georgi Petkov", "Levski Sofia", "1998-05-10", "Bulgarian", "GK", 1),
    PlayerSeed("Ivan Petrov", "Levski Sofia", "2000-04-12", "Bulgarian", "FW", 9),
    PlayerSeed("Martin Raynov", "Levski Sofia", "1996-02-18", "Bulgarian", "MF", 8),
    PlayerSeed("Petar Ivanov", "Levski Sofia", "1999-09-03", "Bulgarian", "DF", 4, "injured"),
    PlayerSeed("Dimitar Evtimov", "CSKA Sofia", "1995-09-07", "Bulgarian", "GK", 1),
    PlayerSeed("Asen Todorov", "CSKA Sofia", "2001-03-19", "Bulgarian", "MF", 7),
    PlayerSeed("Daniel Ivanov", "CSKA Sofia", "1996-08-23", "Bulgarian", "FW", 11),
    PlayerSeed("Martin Dimitrov", "CSKA Sofia", "1998-06-11", "Bulgarian", "DF", 5),
    PlayerSeed("Sergio Padt", "Ludogorets", "1990-06-06", "Dutch", "GK", 1),
    PlayerSeed("Spas Delev", "Ludogorets", "1989-09-22", "Bulgarian", "FW", 90),
    PlayerSeed("Simon Slavchev", "Ludogorets", "1993-09-25", "Bulgarian", "MF", 20),
    PlayerSeed("Anton Nedyalkov", "Ludogorets", "1993-04-30", "Bulgarian", "DF", 3, "suspended"),
    PlayerSeed("Hidajet Hankic", "Botev Plovdiv", "1994-06-29", "Austrian", "GK", 13),
    PlayerSeed("Nikolay Georgiev", "Botev Plovdiv", "2000-01-02", "Bulgarian", "FW", 10),
    PlayerSeed("Todor Nedelev", "Botev Plovdiv", "1993-02-07", "Bulgarian", "MF", 8),
    PlayerSeed("Viktor Genev", "Botev Plovdiv", "1988-10-27", "Bulgarian", "DF", 4),
    PlayerSeed("Ivan Dyulgerov", "Cherno More", "1999-07-15", "Bulgarian", "GK", 25),
    PlayerSeed("Atanas Iliev", "Cherno More", "1994-10-09", "Bulgarian", "FW", 9),
    PlayerSeed("Mazire Soula", "Cherno More", "1998-06-06", "French", "MF", 10),
    PlayerSeed("Tsvetomir Panov", "Cherno More", "1989-04-17", "Bulgarian", "DF", 2),
    PlayerSeed("Dinko Horkas", "Lokomotiv Plovdiv", "1999-03-10", "Croatian", "GK", 23),
    PlayerSeed("Giovanny", "Lokomotiv Plovdiv", "1997-11-11", "Brazilian", "FW", 99),
    PlayerSeed("Petar Vitanov", "Lokomotiv Plovdiv", "1995-03-10", "Bulgarian", "MF", 34),
    PlayerSeed("Martin Paskalev", "Lokomotiv Plovdiv", "2001-02-25", "Bulgarian", "DF", 4),
]

DEMO_RESULTS = [
    (1, "Botev Plovdiv", "Levski Sofia", 1, 2),
    (1, "Cherno More", "CSKA Sofia", 0, 2),
    (1, "Lokomotiv Plovdiv", "Ludogorets", 1, 1),
    (2, "Levski Sofia", "Cherno More", 3, 0),
    (2, "Ludogorets", "Botev Plovdiv", 2, 0),
    (2, "CSKA Sofia", "Lokomotiv Plovdiv", 1, 1),
    (3, "Lokomotiv Plovdiv", "Levski Sofia", 0, 1),
    (3, "Cherno More", "Ludogorets", 2, 2),
    (3, "Botev Plovdiv", "CSKA Sofia", 1, 3),
    (4, "Levski Sofia", "Ludogorets", 2, 2),
    (4, "CSKA Sofia", "Lokomotiv Plovdiv", 2, 0),
    (4, "Botev Plovdiv", "Cherno More", 1, 0),
    (5, "CSKA Sofia", "Levski Sofia", 1, 1),
    (5, "Ludogorets", "Botev Plovdiv", 3, 1),
    (5, "Cherno More", "Lokomotiv Plovdiv", 2, 1),
]

SANDBOX_FIXTURES = [
    (1, "Levski Sofia", "CSKA Sofia"),
    (1, "Ludogorets", "Botev Plovdiv"),
    (1, "Cherno More", "Lokomotiv Plovdiv"),
    (2, "Botev Plovdiv", "Levski Sofia"),
    (2, "Cherno More", "Ludogorets"),
    (2, "Lokomotiv Plovdiv", "CSKA Sofia"),
    (3, "Levski Sofia", "Cherno More"),
    (3, "CSKA Sofia", "Botev Plovdiv"),
    (3, "Ludogorets", "Lokomotiv Plovdiv"),
    (4, "Lokomotiv Plovdiv", "Levski Sofia"),
    (4, "Cherno More", "Botev Plovdiv"),
    (4, "CSKA Sofia", "Ludogorets"),
    (5, "Levski Sofia", "Ludogorets"),
    (5, "Botev Plovdiv", "Lokomotiv Plovdiv"),
    (5, "Cherno More", "CSKA Sofia"),
]

GOAL_EVENTS = [
    ("Botev Plovdiv", "Nikolay Georgiev", 31),
    ("Levski Sofia", "Ivan Petrov", 44),
    ("Levski Sofia", "Ivan Petrov", 78),
    ("CSKA Sofia", "Daniel Ivanov", 12),
    ("CSKA Sofia", "Asen Todorov", 66),
]

CARD_EVENTS = [
    ("Botev Plovdiv", "Viktor Genev", "Y", 54),
    ("Levski Sofia", "Petar Ivanov", "Y", 70),
    ("CSKA Sofia", "Martin Dimitrov", "R", 83),
]

TRANSFERS = [
    ("Daniel Ivanov", "Levski Sofia", "CSKA Sofia", "2025-07-01", 120000.0),
    ("Nikolay Georgiev", "Cherno More", "Botev Plovdiv", "2025-07-15", 45000.0),
    ("Simon Slavchev", "CSKA Sofia", "Ludogorets", "2025-08-02", 70000.0),
]


def seed_full_demo_data() -> str:
    with transaction() as cursor:
        before = _counts(cursor)
        club_ids = _seed_clubs(cursor)
        player_ids = _seed_players(cursor, club_ids)
        demo_league_id = _seed_league(cursor, DEMO_LEAGUE, DEMO_SEASON)
        sandbox_league_id = _seed_league(cursor, SANDBOX_LEAGUE, SANDBOX_SEASON)
        _seed_league_teams(cursor, demo_league_id, club_ids.values())
        _seed_league_teams(cursor, sandbox_league_id, club_ids.values())
        _seed_demo_matches(cursor, demo_league_id, club_ids)
        _seed_sandbox_matches(cursor, sandbox_league_id, club_ids)
        _seed_events(cursor, demo_league_id, club_ids, player_ids)
        _seed_transfers(cursor, club_ids, player_ids)
        after = _counts(cursor)

    added = {key: after[key] - before[key] for key in before}
    if all(value == 0 for value in added.values()):
        return "Full demo seed is already loaded."

    return (
        "Full demo seed loaded: "
        f"{added['clubs']} clubs, {added['players']} players, {added['leagues']} leagues, "
        f"{added['league_teams']} league teams, {added['matches']} matches, "
        f"{added['goals']} goals, {added['cards']} cards, {added['transfers']} transfers."
    )


def seed_summary() -> dict[str, int | str]:
    league = fetch_one("SELECT id FROM leagues WHERE name = ? AND season = ?", (DEMO_LEAGUE, DEMO_SEASON))
    sandbox = fetch_one("SELECT id FROM leagues WHERE name = ? AND season = ?", (SANDBOX_LEAGUE, SANDBOX_SEASON))
    return {
        "played_league": f"{DEMO_LEAGUE} {DEMO_SEASON}",
        "sandbox_league": f"{SANDBOX_LEAGUE} {SANDBOX_SEASON}",
        "demo_matches": _count_where("matches", "league_id = ?", (league["id"],)) if league else 0,
        "sandbox_matches": _count_where("matches", "league_id = ?", (sandbox["id"],)) if sandbox else 0,
        "played_matches": _count_where("matches", "status = 'played'"),
        "scheduled_matches": _count_where("matches", "status = 'scheduled'"),
    }


def clear_database() -> str:
    tables = ["goals", "cards", "transfers", "matches", "league_teams", "players", "leagues", "clubs"]
    with transaction() as cursor:
        before = _counts(cursor)
        cursor.execute("PRAGMA foreign_keys = OFF")
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
        cursor.execute(
            """
            DELETE FROM sqlite_sequence
            WHERE name IN ('clubs', 'players', 'leagues', 'matches', 'goals', 'cards', 'transfers')
            """
        )
        cursor.execute("PRAGMA foreign_keys = ON")

    total_deleted = sum(before.values())
    if total_deleted == 0:
        return "Database is already empty."
    return f"Database cleared: {total_deleted} rows removed."


def _counts(cursor) -> dict[str, int]:
    tables = ["clubs", "players", "leagues", "league_teams", "matches", "goals", "cards", "transfers"]
    result = {}
    for table in tables:
        result[table] = int(cursor.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"])
    return result


def _count_where(table: str, where: str, params: tuple = ()) -> int:
    row = fetch_one(f"SELECT COUNT(*) AS count FROM {table} WHERE {where}", params)
    return int(row["count"]) if row is not None else 0


def _seed_clubs(cursor) -> dict[str, int]:
    for name, city, founded_year in CLUBS:
        cursor.execute(
            "INSERT OR IGNORE INTO clubs (name, city, founded_year) VALUES (?, ?, ?)",
            (name, city, founded_year),
        )
    return _ids_by_name(cursor, "clubs", [name for name, _, _ in CLUBS])


def _seed_players(cursor, club_ids: dict[str, int]) -> dict[str, int]:
    for player in PLAYERS:
        row = cursor.execute(
            "SELECT id FROM players WHERE lower(full_name) = lower(?)",
            (player.name,),
        ).fetchone()
        if row is not None:
            continue
        cursor.execute(
            """
            INSERT INTO players (full_name, birth_date, nationality, position, number, status, club_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                player.name,
                player.birth_date,
                player.nationality,
                player.position,
                player.number,
                player.status,
                club_ids[player.club],
            ),
        )
    return _ids_by_name(cursor, "players", [player.name for player in PLAYERS], column="full_name")


def _seed_league(cursor, name: str, season: str) -> int:
    cursor.execute("INSERT OR IGNORE INTO leagues (name, season) VALUES (?, ?)", (name, season))
    row = cursor.execute("SELECT id FROM leagues WHERE name = ? AND season = ?", (name, season)).fetchone()
    return int(row["id"])


def _seed_league_teams(cursor, league_id: int, club_ids: Iterable[int]) -> None:
    cursor.executemany(
        "INSERT OR IGNORE INTO league_teams (league_id, club_id) VALUES (?, ?)",
        [(league_id, club_id) for club_id in club_ids],
    )


def _seed_demo_matches(cursor, league_id: int, club_ids: dict[str, int]) -> None:
    for round_no, home, away, home_goals, away_goals in DEMO_RESULTS:
        cursor.execute(
            """
            INSERT OR IGNORE INTO matches (
              league_id, round_no, home_club_id, away_club_id, home_goals, away_goals, status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'played')
            """,
            (league_id, round_no, club_ids[home], club_ids[away], home_goals, away_goals),
        )
        cursor.execute(
            """
            UPDATE matches
            SET home_goals = ?, away_goals = ?, status = 'played'
            WHERE league_id = ? AND round_no = ? AND home_club_id = ? AND away_club_id = ?
            """,
            (home_goals, away_goals, league_id, round_no, club_ids[home], club_ids[away]),
        )


def _seed_sandbox_matches(cursor, league_id: int, club_ids: dict[str, int]) -> None:
    for round_no, home, away in SANDBOX_FIXTURES:
        cursor.execute(
            """
            INSERT OR IGNORE INTO matches (league_id, round_no, home_club_id, away_club_id, status)
            VALUES (?, ?, ?, ?, 'scheduled')
            """,
            (league_id, round_no, club_ids[home], club_ids[away]),
        )


def _seed_events(cursor, league_id: int, club_ids: dict[str, int], player_ids: dict[str, int]) -> None:
    match = cursor.execute(
        """
        SELECT id FROM matches
        WHERE league_id = ? AND home_club_id = ? AND away_club_id = ?
        """,
        (league_id, club_ids["Botev Plovdiv"], club_ids["Levski Sofia"]),
    ).fetchone()
    if match is None:
        return
    match_id = int(match["id"])

    for club, player, minute in GOAL_EVENTS:
        if not _event_exists(cursor, "goals", match_id, player_ids[player], minute):
            cursor.execute(
                "INSERT INTO goals (match_id, player_id, club_id, minute) VALUES (?, ?, ?, ?)",
                (match_id, player_ids[player], club_ids[club], minute),
            )

    for club, player, card_type, minute in CARD_EVENTS:
        if not _event_exists(cursor, "cards", match_id, player_ids[player], minute, card_type):
            cursor.execute(
                "INSERT INTO cards (match_id, player_id, club_id, minute, card_type) VALUES (?, ?, ?, ?, ?)",
                (match_id, player_ids[player], club_ids[club], minute, card_type),
            )


def _seed_transfers(cursor, club_ids: dict[str, int], player_ids: dict[str, int]) -> None:
    for player, from_club, to_club, date, fee in TRANSFERS:
        exists = cursor.execute(
            """
            SELECT id FROM transfers
            WHERE player_id = ? AND from_club_id = ? AND to_club_id = ? AND transfer_date = ?
            """,
            (player_ids[player], club_ids[from_club], club_ids[to_club], date),
        ).fetchone()
        if exists is not None:
            continue
        cursor.execute(
            """
            INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (player_ids[player], club_ids[from_club], club_ids[to_club], date, fee, "Seeded demo transfer"),
        )


def _event_exists(cursor, table: str, match_id: int, player_id: int, minute: int, card_type: str | None = None) -> bool:
    if card_type is None:
        row = cursor.execute(
            f"SELECT id FROM {table} WHERE match_id = ? AND player_id = ? AND minute = ?",
            (match_id, player_id, minute),
        ).fetchone()
    else:
        row = cursor.execute(
            f"SELECT id FROM {table} WHERE match_id = ? AND player_id = ? AND minute = ? AND card_type = ?",
            (match_id, player_id, minute, card_type),
        ).fetchone()
    return row is not None


def _ids_by_name(cursor, table: str, names: list[str], column: str = "name") -> dict[str, int]:
    ids = {}
    for name in names:
        row = cursor.execute(f"SELECT id FROM {table} WHERE lower({column}) = lower(?)", (name,)).fetchone()
        ids[name] = int(row["id"])
    return ids
