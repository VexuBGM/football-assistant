from typing import Iterable, Optional

from ..database.db import fetch_all, fetch_one, transaction


def get_league_by_name_and_season(name: str, season: str):
    return fetch_one(
        """
        SELECT id, name, season, created_at
        FROM leagues
        WHERE lower(name) = lower(?) AND season = ?
        """,
        (name, season),
    )


def create_league(name: str, season: str) -> int:
    with transaction() as cursor:
        cursor.execute(
            "INSERT INTO leagues (name, season) VALUES (?, ?)",
            (name, season),
        )
        return int(cursor.lastrowid)


def get_league_teams(league_id: int):
    return fetch_all(
        """
        SELECT c.id, c.name, c.city, c.founded_year
        FROM league_teams lt
        JOIN clubs c ON c.id = lt.club_id
        WHERE lt.league_id = ?
        ORDER BY c.name ASC
        """,
        (league_id,),
    )


def is_team_in_league(league_id: int, club_id: int) -> bool:
    row = fetch_one(
        "SELECT 1 FROM league_teams WHERE league_id = ? AND club_id = ?",
        (league_id, club_id),
    )
    return row is not None


def add_team_to_league(league_id: int, club_id: int) -> None:
    with transaction() as cursor:
        cursor.execute(
            "INSERT INTO league_teams (league_id, club_id) VALUES (?, ?)",
            (league_id, club_id),
        )


def remove_team_from_league(league_id: int, club_id: int) -> None:
    with transaction() as cursor:
        cursor.execute(
            "DELETE FROM league_teams WHERE league_id = ? AND club_id = ?",
            (league_id, club_id),
        )


def count_matches_for_league(league_id: int) -> int:
    row = fetch_one("SELECT COUNT(*) AS count FROM matches WHERE league_id = ?", (league_id,))
    return int(row["count"]) if row is not None else 0


def insert_matches(league_id: int, matches: Iterable[dict[str, int]]) -> None:
    with transaction() as cursor:
        cursor.executemany(
            """
            INSERT INTO matches (league_id, round_no, home_club_id, away_club_id, match_date, home_goals, away_goals)
            VALUES (?, ?, ?, ?, NULL, NULL, NULL)
            """,
            [
                (
                    league_id,
                    match["round_no"],
                    match["home_club_id"],
                    match["away_club_id"],
                )
                for match in matches
            ],
        )


def get_matches_for_league(league_id: int):
    return fetch_all(
        """
        SELECT
          m.round_no,
          home.name AS home_name,
          away.name AS away_name
        FROM matches m
        JOIN clubs home ON home.id = m.home_club_id
        JOIN clubs away ON away.id = m.away_club_id
        WHERE m.league_id = ?
        ORDER BY m.round_no ASC, m.id ASC
        """,
        (league_id,),
    )
