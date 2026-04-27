from typing import Optional

from ..repositories import matches_repo
from .clubs_service import resolve_club
from .leagues_service import find_league, normalize_text as normalize_league_text
from .players_service import find_player, normalize_text

VALID_CARD_TYPES = {"Y", "R"}


def _format_score(match_row: dict[str, object]) -> str:
    if match_row["home_goals"] is None or match_row["away_goals"] is None:
        return "vs"
    return f'{match_row["home_goals"]}:{match_row["away_goals"]}'


def _match_summary(match_row: dict[str, object]) -> str:
    return (
        f'#{match_row["id"]} {match_row["home_name"]} vs {match_row["away_name"]} '
        f'[{match_row["status"]}] {_format_score(match_row)}'
    )


def _validate_minute(minute: int) -> Optional[str]:
    if not 1 <= minute <= 120:
        return "Minute must be between 1 and 120."
    return None


def _resolve_player_and_club(subject_text: str) -> tuple[Optional[dict[str, object]], Optional[dict[str, object]], Optional[str]]:
    tokens = normalize_text(subject_text).split()
    if len(tokens) < 2:
        return None, None, "Command must include both player and club."

    for split_index in range(1, len(tokens)):
        player_name = " ".join(tokens[:split_index])
        club_name = " ".join(tokens[split_index:])
        player = find_player(player_name)
        club = resolve_club(club_name)
        if player is not None and club is not None:
            return player, club, None

    return None, None, f'Could not resolve player and club from "{normalize_text(subject_text)}".'


def _resolve_match(match_id: int) -> Optional[dict[str, object]]:
    row = matches_repo.get_match_by_id(match_id)
    if row is None:
        return None
    return dict(row)


def _validate_match_participant(match_row: dict[str, object], club_id: int) -> bool:
    return club_id in {match_row["home_club_id"], match_row["away_club_id"]}


def show_round(league_name: str, season: str, round_no: int) -> str:
    if round_no <= 0:
        return "Round number must be a positive integer."

    league = find_league(league_name, season)
    if league is None:
        return f'Няма лига с име "{normalize_league_text(league_name)}" сезон {normalize_league_text(season)}.'

    rows = [dict(row) for row in matches_repo.get_round_matches(int(league["id"]), round_no)]
    if not rows:
        return f'Няма мачове за кръг {round_no} в лига "{league["name"]}" сезон {league["season"]}.'

    lines = [f'Кръг {round_no} | лига "{league["name"]}" сезон {league["season"]}:']
    for row in rows:
        score = _format_score(row)
        lines.append(
            f'- match #{row["id"]}: {row["home_name"]} vs {row["away_name"]} | status {row["status"]} | result {score}'
        )
    return "\n".join(lines)


def select_match(match_id: int) -> str:
    match_row = _resolve_match(match_id)
    if match_row is None:
        return f"No match with ID {match_id}."

    return (
        f'Selected match #{match_row["id"]}: {match_row["home_name"]} vs {match_row["away_name"]} '
        f'| league "{match_row["league_name"]}" {match_row["league_season"]} | round {match_row["round_no"]}.'
    )


def record_result(league_name: str, season: str, home_team: str, away_team: str, home_goals: int, away_goals: int) -> str:
    if home_goals < 0 or away_goals < 0:
        return "Goals in a result must be whole numbers greater than or equal to 0."

    league = find_league(league_name, season)
    if league is None:
        return f'Няма лига с име "{normalize_league_text(league_name)}" сезон {normalize_league_text(season)}.'

    home_club = resolve_club(home_team)
    if home_club is None:
        return f"No club found: {normalize_text(home_team)}"

    away_club = resolve_club(away_team)
    if away_club is None:
        return f"No club found: {normalize_text(away_team)}"

    if home_club["id"] == away_club["id"]:
        return "Result failed: home and away teams must be different."

    matches = [
        dict(row)
        for row in matches_repo.find_match_in_league_by_teams(
            int(league["id"]),
            int(home_club["id"]),
            int(away_club["id"]),
        )
    ]
    if not matches:
        return (
            f'No scheduled match found for {home_club["name"]} vs {away_club["name"]} '
            f'in league "{league["name"]}" season {league["season"]}.'
        )
    if len(matches) != 1:
        return "Result failed: more than one match matches these teams in the current league context."

    match_row = matches[0]
    if match_row["status"] == "played":
        return f'Match #{match_row["id"]} already has a saved result.'

    matches_repo.update_match_result(int(match_row["id"]), home_goals, away_goals)
    return (
        f'Saved result: {home_club["name"]}-{away_club["name"]} {home_goals}:{away_goals} '
        f'(match #{match_row["id"]}, round {match_row["round_no"]}).'
    )


def add_goal(match_id: int, player_name: str, club_name: str, minute: int) -> str:
    minute_error = _validate_minute(minute)
    if minute_error is not None:
        return minute_error

    match_row = _resolve_match(match_id)
    if match_row is None:
        return f"No match with ID {match_id}."

    club = resolve_club(club_name)
    if club is None:
        return f"No club found: {normalize_text(club_name)}"
    if not _validate_match_participant(match_row, int(club["id"])):
        return f'Club "{club["name"]}" does not participate in match #{match_id}.'

    player = find_player(player_name)
    if player is None:
        return f"No player found: {normalize_text(player_name)}"
    if player["club_id"] != club["id"]:
        return f'{player["full_name"]} does not belong to {club["name"]}.'
    if not _validate_match_participant(match_row, int(player["club_id"])):
        return f'{player["full_name"]} is not from one of the teams in match #{match_id}.'

    goal_id = matches_repo.add_goal(match_id, int(player["id"]), int(club["id"]), minute)
    return (
        f'Goal added: {player["full_name"]} for {club["name"]} in minute {minute} '
        f'(match #{match_id}, goal #{goal_id}).'
    )


def add_goal_from_text(match_id: int, subject_text: str, minute: int) -> str:
    player, club, error = _resolve_player_and_club(subject_text)
    if error is not None:
        return error
    return add_goal(match_id, str(player["full_name"]), str(club["name"]), minute)


def add_card(match_id: int, player_name: str, club_name: str, card_type: str, minute: int) -> str:
    minute_error = _validate_minute(minute)
    if minute_error is not None:
        return minute_error

    card_value = normalize_text(card_type).upper()
    if card_value not in VALID_CARD_TYPES:
        return "Card type must be Y or R."

    match_row = _resolve_match(match_id)
    if match_row is None:
        return f"No match with ID {match_id}."

    club = resolve_club(club_name)
    if club is None:
        return f"No club found: {normalize_text(club_name)}"
    if not _validate_match_participant(match_row, int(club["id"])):
        return f'Club "{club["name"]}" does not participate in match #{match_id}.'

    player = find_player(player_name)
    if player is None:
        return f"No player found: {normalize_text(player_name)}"
    if player["club_id"] != club["id"]:
        return f'{player["full_name"]} does not belong to {club["name"]}.'

    if card_value == "R" and matches_repo.count_cards_for_player(match_id, int(player["id"]), "R") >= 1:
        return f'{player["full_name"]} already has a red card in match #{match_id}.'

    card_id = matches_repo.add_card(match_id, int(player["id"]), int(club["id"]), minute, card_value)
    return (
        f'Card added: {player["full_name"]} ({club["name"]}) {card_value} in minute {minute} '
        f'(match #{match_id}, card #{card_id}).'
    )


def add_card_from_text(match_id: int, subject_text: str, card_type: str, minute: int) -> str:
    player, club, error = _resolve_player_and_club(subject_text)
    if error is not None:
        return error
    return add_card(match_id, str(player["full_name"]), str(club["name"]), card_type, minute)


def show_events(match_id: int) -> str:
    match_row = _resolve_match(match_id)
    if match_row is None:
        return f"No match with ID {match_id}."

    rows = [dict(row) for row in matches_repo.get_match_events(match_id)]
    if not rows:
        return f'No events recorded for match #{match_id} ({match_row["home_name"]} vs {match_row["away_name"]}).'

    lines = [f'Events for match #{match_id} ({match_row["home_name"]} vs {match_row["away_name"]}):']
    for row in rows:
        if row["event_type"] == "goal":
            lines.append(f'- {row["minute"]}\' GOAL | {row["player_name"]} | {row["club_name"]}')
        else:
            lines.append(f'- {row["minute"]}\' CARD {row["card_type"]} | {row["player_name"]} | {row["club_name"]}')
    return "\n".join(lines)
