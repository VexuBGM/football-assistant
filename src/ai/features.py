from dataclasses import dataclass
from typing import Any

from ..repositories import ai_repo
from ..services import clubs_service, standings_service

MIN_TEAM_MATCHES = 5


@dataclass(frozen=True)
class TeamFeatures:
    club_id: int
    name: str
    matches_played: int
    last_five_points: int
    form_ratio: float
    avg_goals_for: float
    avg_goals_against: float
    standing_position: int
    standing_points: int
    strength_index: float


@dataclass(frozen=True)
class PredictionFeatures:
    league_name: str
    season: str
    home: TeamFeatures
    away: TeamFeatures


def build_prediction_features(home_team: str, away_team: str) -> tuple[PredictionFeatures | None, str | None]:
    home_club = clubs_service.resolve_club(home_team)
    if home_club is None:
        return None, f'Отборът "{home_team}" не съществува.'

    away_club = clubs_service.resolve_club(away_team)
    if away_club is None:
        return None, f'Отборът "{away_team}" не съществува.'

    if int(home_club["id"]) == int(away_club["id"]):
        return None, "Не може да се прогнозира мач на отбор срещу самия себе си."

    common_leagues = [dict(row) for row in ai_repo.get_common_leagues(int(home_club["id"]), int(away_club["id"]))]
    if not common_leagues:
        return None, (
            f'Отборите "{home_club["name"]}" и "{away_club["name"]}" не са в една и съща лига.'
        )

    last_error: str | None = None
    for league in common_leagues:
        features, error = _build_features_for_league(dict(home_club), dict(away_club), league)
        if features is not None:
            return features, None
        last_error = error

    return None, last_error


def _build_features_for_league(
    home_club: dict[str, Any],
    away_club: dict[str, Any],
    league: dict[str, Any],
) -> tuple[PredictionFeatures | None, str | None]:
    rows, standings_error = standings_service.calculate_standings(str(league["name"]), str(league["season"]))
    if standings_error is not None:
        return None, standings_error

    played_matches = [dict(row) for row in ai_repo.get_played_matches_for_league(int(league["id"]))]
    home_matches = _matches_for_team(played_matches, int(home_club["id"]))
    away_matches = _matches_for_team(played_matches, int(away_club["id"]))

    if len(home_matches) < MIN_TEAM_MATCHES or len(away_matches) < MIN_TEAM_MATCHES:
        return None, (
            f'Недостатъчно данни за прогноза в лига "{league["name"]}" сезон {league["season"]}: '
            f'нужни са поне {MIN_TEAM_MATCHES} изиграни мача за всеки отбор '
            f'({home_club["name"]}: {len(home_matches)}, {away_club["name"]}: {len(away_matches)}).'
        )

    positions = {row.club_id: index for index, row in enumerate(rows, start=1)}
    team_count = len(rows)
    standings_by_id = {row.club_id: row for row in rows}

    home_features = _team_features(dict(home_club), home_matches, positions, standings_by_id, team_count)
    away_features = _team_features(dict(away_club), away_matches, positions, standings_by_id, team_count)
    return (
        PredictionFeatures(
            league_name=str(league["name"]),
            season=str(league["season"]),
            home=home_features,
            away=away_features,
        ),
        None,
    )


def _matches_for_team(matches: list[dict[str, Any]], club_id: int) -> list[dict[str, Any]]:
    return [row for row in matches if int(row["home_club_id"]) == club_id or int(row["away_club_id"]) == club_id]


def _team_features(
    club: dict[str, Any],
    matches: list[dict[str, Any]],
    positions: dict[int, int],
    standings_by_id: dict[int, standings_service.StandingRow],
    team_count: int,
) -> TeamFeatures:
    club_id = int(club["id"])
    last_five = matches[-MIN_TEAM_MATCHES:]
    last_five_points = sum(_points_for_team(row, club_id) for row in last_five)
    goals_for = sum(_goals_for_team(row, club_id) for row in matches)
    goals_against = sum(_goals_against_team(row, club_id) for row in matches)
    avg_goals_for = goals_for / len(matches)
    avg_goals_against = goals_against / len(matches)
    position = positions[club_id]
    standing = standings_by_id[club_id]
    strength_index = _strength_index(
        form_ratio=last_five_points / 15,
        avg_goals_for=avg_goals_for,
        avg_goals_against=avg_goals_against,
        standing_position=position,
        team_count=team_count,
    )

    return TeamFeatures(
        club_id=club_id,
        name=str(club["name"]),
        matches_played=len(matches),
        last_five_points=last_five_points,
        form_ratio=last_five_points / 15,
        avg_goals_for=avg_goals_for,
        avg_goals_against=avg_goals_against,
        standing_position=position,
        standing_points=standing.points,
        strength_index=strength_index,
    )


def _goals_for_team(match: dict[str, Any], club_id: int) -> int:
    if int(match["home_club_id"]) == club_id:
        return int(match["home_goals"])
    return int(match["away_goals"])


def _goals_against_team(match: dict[str, Any], club_id: int) -> int:
    if int(match["home_club_id"]) == club_id:
        return int(match["away_goals"])
    return int(match["home_goals"])


def _points_for_team(match: dict[str, Any], club_id: int) -> int:
    gf = _goals_for_team(match, club_id)
    ga = _goals_against_team(match, club_id)
    if gf > ga:
        return 3
    if gf == ga:
        return 1
    return 0


def _strength_index(
    form_ratio: float,
    avg_goals_for: float,
    avg_goals_against: float,
    standing_position: int,
    team_count: int,
) -> float:
    attack_score = min(avg_goals_for / 3, 1.0)
    defense_score = 1 / (1 + avg_goals_against)
    standing_score = (team_count - standing_position + 1) / team_count
    return (form_ratio * 0.45) + (attack_score * 0.25) + (defense_score * 0.15) + (standing_score * 0.15)
