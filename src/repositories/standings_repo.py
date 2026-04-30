from ..database.db import fetch_all


def get_league_teams(league_id: int):
    return fetch_all(
        """
        SELECT c.id, c.name
        FROM league_teams lt
        JOIN clubs c ON c.id = lt.club_id
        WHERE lt.league_id = ?
        ORDER BY c.name ASC
        """,
        (league_id,),
    )


def get_league_matches(league_id: int):
    return fetch_all(
        """
        SELECT
          m.id,
          m.home_club_id,
          home.name AS home_name,
          m.away_club_id,
          away.name AS away_name,
          m.home_goals,
          m.away_goals,
          m.status
        FROM matches m
        JOIN clubs home ON home.id = m.home_club_id
        JOIN clubs away ON away.id = m.away_club_id
        WHERE m.league_id = ?
        ORDER BY m.id ASC
        """,
        (league_id,),
    )
