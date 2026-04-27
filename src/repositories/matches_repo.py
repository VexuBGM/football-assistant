from typing import Optional

from ..database.db import fetch_all, fetch_one, transaction


def get_round_matches(league_id: int, round_no: int):
    return fetch_all(
        """
        SELECT
          m.id,
          m.round_no,
          m.home_goals,
          m.away_goals,
          m.status,
          home.id AS home_club_id,
          home.name AS home_name,
          away.id AS away_club_id,
          away.name AS away_name
        FROM matches m
        JOIN clubs home ON home.id = m.home_club_id
        JOIN clubs away ON away.id = m.away_club_id
        WHERE m.league_id = ? AND m.round_no = ?
        ORDER BY m.id ASC
        """,
        (league_id, round_no),
    )


def get_match_by_id(match_id: int):
    return fetch_one(
        """
        SELECT
          m.id,
          m.league_id,
          m.round_no,
          m.match_date,
          m.home_goals,
          m.away_goals,
          m.status,
          l.name AS league_name,
          l.season AS league_season,
          home.id AS home_club_id,
          home.name AS home_name,
          away.id AS away_club_id,
          away.name AS away_name
        FROM matches m
        JOIN leagues l ON l.id = m.league_id
        JOIN clubs home ON home.id = m.home_club_id
        JOIN clubs away ON away.id = m.away_club_id
        WHERE m.id = ?
        """,
        (match_id,),
    )


def find_match_in_league_by_teams(league_id: int, home_club_id: int, away_club_id: int):
    return fetch_all(
        """
        SELECT
          m.id,
          m.league_id,
          m.round_no,
          m.home_goals,
          m.away_goals,
          m.status,
          home.id AS home_club_id,
          home.name AS home_name,
          away.id AS away_club_id,
          away.name AS away_name
        FROM matches m
        JOIN clubs home ON home.id = m.home_club_id
        JOIN clubs away ON away.id = m.away_club_id
        WHERE m.league_id = ? AND m.home_club_id = ? AND m.away_club_id = ?
        """,
        (league_id, home_club_id, away_club_id),
    )


def update_match_result(match_id: int, home_goals: int, away_goals: int) -> None:
    with transaction() as cursor:
        cursor.execute(
            """
            UPDATE matches
            SET home_goals = ?, away_goals = ?, status = 'played'
            WHERE id = ?
            """,
            (home_goals, away_goals, match_id),
        )


def add_goal(match_id: int, player_id: int, club_id: int, minute: int, is_own_goal: int = 0) -> int:
    with transaction() as cursor:
        cursor.execute(
            """
            INSERT INTO goals (match_id, player_id, club_id, minute, is_own_goal)
            VALUES (?, ?, ?, ?, ?)
            """,
            (match_id, player_id, club_id, minute, is_own_goal),
        )
        return int(cursor.lastrowid)


def add_card(match_id: int, player_id: int, club_id: int, minute: int, card_type: str) -> int:
    with transaction() as cursor:
        cursor.execute(
            """
            INSERT INTO cards (match_id, player_id, club_id, minute, card_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (match_id, player_id, club_id, minute, card_type),
        )
        return int(cursor.lastrowid)


def get_match_events(match_id: int):
    return fetch_all(
        """
        SELECT
          minute,
          sort_group,
          event_id,
          event_type,
          player_name,
          club_name,
          card_type
        FROM (
          SELECT
            g.minute AS minute,
            1 AS sort_group,
            g.id AS event_id,
            'goal' AS event_type,
            p.full_name AS player_name,
            c.name AS club_name,
            NULL AS card_type
          FROM goals g
          JOIN players p ON p.id = g.player_id
          JOIN clubs c ON c.id = g.club_id
          WHERE g.match_id = ?

          UNION ALL

          SELECT
            c2.minute AS minute,
            2 AS sort_group,
            c2.id AS event_id,
            'card' AS event_type,
            p.full_name AS player_name,
            c.name AS club_name,
            c2.card_type AS card_type
          FROM cards c2
          JOIN players p ON p.id = c2.player_id
          JOIN clubs c ON c.id = c2.club_id
          WHERE c2.match_id = ?
        )
        ORDER BY minute ASC, sort_group ASC, event_id ASC
        """,
        (match_id, match_id),
    )


def count_cards_for_player(match_id: int, player_id: int, card_type: Optional[str] = None) -> int:
    if card_type is None:
        row = fetch_one(
            "SELECT COUNT(*) AS count FROM cards WHERE match_id = ? AND player_id = ?",
            (match_id, player_id),
        )
    else:
        row = fetch_one(
            "SELECT COUNT(*) AS count FROM cards WHERE match_id = ? AND player_id = ? AND card_type = ?",
            (match_id, player_id, card_type),
        )
    return int(row["count"]) if row is not None else 0
