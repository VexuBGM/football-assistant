import re
from collections import defaultdict
from typing import Optional

from ..repositories import leagues_repo
from .clubs_service import resolve_club

MIN_TEAMS_FOR_SCHEDULE = 4
SEASON_PATTERN = re.compile(r"^(\d{4})/(\d{4})$")
BYE = None


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def validate_season(season: str) -> Optional[str]:
    normalized = normalize_text(season)
    match = SEASON_PATTERN.fullmatch(normalized)
    if match is None:
        return None

    start_year = int(match.group(1))
    end_year = int(match.group(2))
    if end_year != start_year + 1:
        return None
    return normalized


def find_league(name: str, season: str) -> Optional[dict[str, object]]:
    league_name = normalize_text(name)
    season_value = validate_season(season)
    if not league_name or season_value is None:
        return None

    row = leagues_repo.get_league_by_name_and_season(league_name, season_value)
    if row is None:
        return None

    return dict(row)


def create_league(name: str, season: str) -> str:
    league_name = normalize_text(name)
    season_value = validate_season(season)

    if not league_name:
        return "Error: league name cannot be empty."
    if season_value is None:
        return "Invalid season format. Use YYYY/YYYY."
    if find_league(league_name, season_value) is not None:
        return f'League "{league_name}" for season {season_value} already exists.'

    league_id = leagues_repo.create_league(league_name, season_value)
    return f'Created league [{league_id}] "{league_name}" for season {season_value}.'


def add_team_to_league(club_identifier: str, league_name: str, season: str) -> str:
    club = resolve_club(club_identifier)
    if club is None:
        return 'Клубът не съществува. Използвай: "Покажи всички клубове".'

    league = find_league(league_name, season)
    if league is None:
        return f'Няма лига с име "{normalize_text(league_name)}" сезон {normalize_text(season)}.'

    if leagues_repo.is_team_in_league(int(league["id"]), int(club["id"])):
        return f'Отборът "{club["name"]}" вече е добавен в лига "{league["name"]}" сезон {league["season"]}.'

    leagues_repo.add_team_to_league(int(league["id"]), int(club["id"]))
    return f'Добавен е отбор "{club["name"]}" в лига "{league["name"]}" сезон {league["season"]}.'


def list_league_teams(league_name: str, season: str) -> str:
    league = find_league(league_name, season)
    if league is None:
        return f'Няма лига с име "{normalize_text(league_name)}" сезон {normalize_text(season)}.'

    teams = leagues_repo.get_league_teams(int(league["id"]))
    if not teams:
        return f'Няма добавени отбори в лига "{league["name"]}" сезон {league["season"]}.'

    lines = [f'Отбори в лига "{league["name"]}" сезон {league["season"]}:']
    for team in teams:
        lines.append(f'- [{team["id"]}] {team["name"]}')
    return "\n".join(lines)


def remove_team_from_league(club_identifier: str, league_name: str, season: str) -> str:
    club = resolve_club(club_identifier)
    if club is None:
        return 'Клубът не съществува. Използвай: "Покажи всички клубове".'

    league = find_league(league_name, season)
    if league is None:
        return f'Няма лига с име "{normalize_text(league_name)}" сезон {normalize_text(season)}.'

    league_id = int(league["id"])
    if not leagues_repo.is_team_in_league(league_id, int(club["id"])):
        return f'Отборът "{club["name"]}" не е част от лига "{league["name"]}" сезон {league["season"]}.'

    if leagues_repo.count_matches_for_league(league_id) > 0:
        return "Не може да премахнеш отбор, защото вече има генерирана програма за тази лига."

    leagues_repo.remove_team_from_league(league_id, int(club["id"]))
    return f'Премахнат е отбор "{club["name"]}" от лига "{league["name"]}" сезон {league["season"]}.'


def _build_round_robin_pairs(team_ids: list[int]) -> list[list[tuple[int, int]]]:
    rotation: list[Optional[int]] = team_ids[:]
    if len(rotation) % 2 == 1:
        rotation.append(BYE)

    total_slots = len(rotation)
    total_rounds = total_slots - 1
    rounds: list[list[tuple[int, int]]] = []

    for round_index in range(total_rounds):
        pairings: list[tuple[int, int]] = []
        for index in range(total_slots // 2):
            home = rotation[index]
            away = rotation[total_slots - 1 - index]
            if home is BYE or away is BYE:
                continue
            if round_index % 2 == 0:
                pairings.append((int(home), int(away)))
            else:
                pairings.append((int(away), int(home)))

        rounds.append(pairings)
        rotation = [rotation[0], rotation[-1], *rotation[1:-1]]

    return rounds


def generate_schedule(league_name: str, season: str) -> str:
    league = find_league(league_name, season)
    if league is None:
        return f'Няма лига с име "{normalize_text(league_name)}" сезон {normalize_text(season)}.'

    league_id = int(league["id"])
    existing_matches = leagues_repo.count_matches_for_league(league_id)
    if existing_matches > 0:
        return "Програма вече е генерирана за тази лига. Изтрий я или добави изрична команда за прегенериране."

    teams = leagues_repo.get_league_teams(league_id)
    if len(teams) < MIN_TEAMS_FOR_SCHEDULE:
        return f"Недостатъчно отбори за програма (минимум {MIN_TEAMS_FOR_SCHEDULE})."

    team_ids = [int(team["id"]) for team in teams]
    rounds = _build_round_robin_pairs(team_ids)

    seen_pairs: set[frozenset[int]] = set()
    prepared_matches: list[dict[str, int]] = []
    for round_no, pairings in enumerate(rounds, start=1):
        round_team_ids: set[int] = set()
        for home_id, away_id in pairings:
            if home_id == away_id:
                return "Internal error: generated invalid self-match."
            pair_key = frozenset((home_id, away_id))
            if pair_key in seen_pairs:
                return "Internal error: generated duplicate match."
            if home_id in round_team_ids or away_id in round_team_ids:
                return "Internal error: generated duplicate team in round."

            seen_pairs.add(pair_key)
            round_team_ids.add(home_id)
            round_team_ids.add(away_id)
            prepared_matches.append(
                {
                    "round_no": round_no,
                    "home_club_id": home_id,
                    "away_club_id": away_id,
                }
            )

    leagues_repo.insert_matches(league_id, prepared_matches)

    teams_by_id = {int(team["id"]): team["name"] for team in teams}
    rounds_map: dict[int, list[str]] = defaultdict(list)
    for match in prepared_matches:
        rounds_map[match["round_no"]].append(
            f'{teams_by_id[match["home_club_id"]]} vs {teams_by_id[match["away_club_id"]]}'
        )

    sample_round = "; ".join(rounds_map[1]) if rounds_map else "No matches"
    return (
        f'Генерирана е програма за лига "{league["name"]}" сезон {league["season"]}. '
        f"Кръгове: {len(rounds)}. Мачове: {len(prepared_matches)}. "
        f"Първи кръг: {sample_round}"
    )
