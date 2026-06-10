from __future__ import annotations

from typing import Any

from ..ai.ai_service import predict_match
from ..database.db import fetch_all, fetch_one
from ..repositories import leagues_repo, matches_repo
from ..services.leagues_service import find_league
from ..services.standings_service import calculate_standings


def _rows(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    return [dict(row) for row in fetch_all(sql, params)]


def dashboard_counts() -> dict[str, int]:
    tables = {
        "clubs": "clubs",
        "players": "players",
        "leagues": "leagues",
        "scheduled_matches": "matches WHERE status = 'scheduled'",
        "played_matches": "matches WHERE status = 'played'",
        "transfers": "transfers",
    }
    counts: dict[str, int] = {}
    for key, table in tables.items():
        row = fetch_one(f"SELECT COUNT(*) AS count FROM {table}")
        counts[key] = int(row["count"]) if row is not None else 0
    return counts


def recent_results(limit: int = 8) -> list[dict[str, Any]]:
    return _rows(
        """
        SELECT
          m.id,
          l.name AS league,
          l.season,
          m.round_no,
          home.name AS home,
          away.name AS away,
          m.home_goals,
          m.away_goals
        FROM matches m
        JOIN leagues l ON l.id = m.league_id
        JOIN clubs home ON home.id = m.home_club_id
        JOIN clubs away ON away.id = m.away_club_id
        WHERE m.status = 'played'
        ORDER BY m.id DESC
        LIMIT ?
        """,
        (limit,),
    )


def list_clubs() -> list[dict[str, Any]]:
    return _rows("SELECT id, name, city, founded_year FROM clubs ORDER BY name ASC")


def club_options() -> list[str]:
    return [row["name"] for row in list_clubs()]


def list_players(club_name: str | None = None) -> list[dict[str, Any]]:
    params: tuple[Any, ...] = ()
    where = ""
    if club_name:
        where = "WHERE lower(c.name) = lower(?)"
        params = (club_name,)
    return _rows(
        f"""
        SELECT
          p.id,
          p.full_name,
          p.birth_date,
          p.nationality,
          p.position,
          p.number,
          p.status,
          COALESCE(c.name, 'Free agent') AS club
        FROM players p
        LEFT JOIN clubs c ON c.id = p.club_id
        {where}
        ORDER BY club ASC, p.number ASC, p.full_name ASC
        """,
        params,
    )


def player_options() -> list[str]:
    return [row["full_name"] for row in list_players()]


def list_leagues() -> list[dict[str, Any]]:
    return _rows(
        """
        SELECT
          l.id,
          l.name,
          l.season,
          COUNT(DISTINCT lt.club_id) AS teams,
          COUNT(DISTINCT m.id) AS matches
        FROM leagues l
        LEFT JOIN league_teams lt ON lt.league_id = l.id
        LEFT JOIN matches m ON m.league_id = l.id
        GROUP BY l.id
        ORDER BY l.season DESC, l.name ASC
        """
    )


def league_options() -> list[str]:
    return [f'{row["name"]} | {row["season"]}' for row in list_leagues()]


def parse_league_option(option: str | None) -> tuple[str | None, str | None]:
    if not option or " | " not in option:
        return None, None
    name, season = option.rsplit(" | ", 1)
    return name, season


def list_league_teams(league_name: str | None, season: str | None) -> list[dict[str, Any]]:
    if not league_name or not season:
        return []
    league = find_league(league_name, season)
    if league is None:
        return []
    return [dict(row) for row in leagues_repo.get_league_teams(int(league["id"]))]


def max_round(league_name: str | None, season: str | None) -> int:
    if not league_name or not season:
        return 1
    league = find_league(league_name, season)
    if league is None:
        return 1
    row = fetch_one("SELECT COALESCE(MAX(round_no), 1) AS max_round FROM matches WHERE league_id = ?", (league["id"],))
    return int(row["max_round"]) if row is not None else 1


def list_matches(league_name: str | None, season: str | None, round_no: int | None = None) -> list[dict[str, Any]]:
    if not league_name or not season:
        return []
    league = find_league(league_name, season)
    if league is None:
        return []
    if round_no is None:
        rows = _rows(
            """
            SELECT
              m.id,
              m.round_no,
              m.status,
              home.name AS home,
              away.name AS away,
              m.home_goals,
              m.away_goals
            FROM matches m
            JOIN clubs home ON home.id = m.home_club_id
            JOIN clubs away ON away.id = m.away_club_id
            WHERE m.league_id = ?
            ORDER BY m.round_no ASC, m.id ASC
            """,
            (league["id"],),
        )
    else:
        rows = [dict(row) for row in matches_repo.get_round_matches(int(league["id"]), round_no)]
        for row in rows:
            row["home"] = row.pop("home_name")
            row["away"] = row.pop("away_name")

    for row in rows:
        if row["home_goals"] is None or row["away_goals"] is None:
            row["score"] = "-"
        else:
            row["score"] = f'{row["home_goals"]}:{row["away_goals"]}'
    return rows


def match_details(match_id: int | None) -> dict[str, Any] | None:
    if match_id is None:
        return None
    row = matches_repo.get_match_by_id(match_id)
    if row is None:
        return None
    data = dict(row)
    data["score"] = "-" if data["home_goals"] is None else f'{data["home_goals"]}:{data["away_goals"]}'
    return data


def match_events(match_id: int | None) -> list[dict[str, Any]]:
    if match_id is None:
        return []
    rows = [dict(row) for row in matches_repo.get_match_events(match_id)]
    for row in rows:
        row["label"] = "Goal" if row["event_type"] == "goal" else f'{row["card_type"]} card'
    return rows


def standings_rows(league_name: str | None, season: str | None) -> tuple[list[dict[str, Any]], str | None]:
    if not league_name or not season:
        return [], "Choose a league first."
    rows, error = calculate_standings(league_name, season)
    if error is not None:
        return [], error
    return [
        {
            "pos": index,
            "team": row.team,
            "mp": row.mp,
            "w": row.wins,
            "d": row.draws,
            "l": row.losses,
            "gf_ga": f"{row.gf}:{row.ga}",
            "gd": row.gd,
            "pts": row.points,
        }
        for index, row in enumerate(rows, start=1)
    ], None


def list_transfers() -> list[dict[str, Any]]:
    return _rows(
        """
        SELECT
          t.id,
          t.transfer_date,
          p.full_name AS player,
          COALESCE(from_club.name, 'Free agent') AS from_club,
          to_club.name AS to_club,
          t.fee
        FROM transfers t
        JOIN players p ON p.id = t.player_id
        LEFT JOIN clubs from_club ON from_club.id = t.from_club_id
        JOIN clubs to_club ON to_club.id = t.to_club_id
        ORDER BY t.transfer_date DESC, t.id DESC
        """
    )


def prediction_view(home: str, away: str) -> tuple[dict[str, Any] | None, str | None]:
    prediction, error = predict_match(home, away)
    if prediction is None:
        return None, error
    return {
        "league": prediction.league_name,
        "season": prediction.season,
        "home": prediction.home_team,
        "away": prediction.away_team,
        "home_win": prediction.home_win,
        "draw": prediction.draw,
        "away_win": prediction.away_win,
        "home_form": prediction.features.home.last5_points,
        "away_form": prediction.features.away.last5_points,
        "home_rank": prediction.features.home.standings_position,
        "away_rank": prediction.features.away.standings_position,
    }, None
