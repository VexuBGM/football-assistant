from ..database.db import fetch_all


def get_common_leagues(home_club_id: int, away_club_id: int):
    return fetch_all(
        """
        SELECT l.id, l.name, l.season
        FROM leagues l
        JOIN league_teams home_lt
          ON home_lt.league_id = l.id AND home_lt.club_id = ?
        JOIN league_teams away_lt
          ON away_lt.league_id = l.id AND away_lt.club_id = ?
        ORDER BY l.season DESC, l.name ASC
        """,
        (home_club_id, away_club_id),
    )


def get_played_matches_for_league(league_id: int):
    return fetch_all(
        """
        SELECT
          m.id,
          m.round_no,
          m.home_club_id,
          home.name AS home_name,
          m.away_club_id,
          away.name AS away_name,
          m.home_goals,
          m.away_goals
        FROM matches m
        JOIN clubs home ON home.id = m.home_club_id
        JOIN clubs away ON away.id = m.away_club_id
        WHERE
          m.league_id = ?
          AND m.status = 'played'
          AND m.home_goals IS NOT NULL
          AND m.away_goals IS NOT NULL
        ORDER BY m.round_no ASC, m.id ASC
        """,
        (league_id,),
    )
