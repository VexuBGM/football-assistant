from dataclasses import dataclass

from ..repositories import standings_repo
from .leagues_service import find_league, normalize_text


@dataclass
class StandingRow:
    club_id: int
    team: str
    mp: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    gf: int = 0
    ga: int = 0
    points: int = 0

    @property
    def gd(self) -> int:
        return self.gf - self.ga


def _apply_match(home: StandingRow, away: StandingRow, home_goals: int, away_goals: int) -> None:
    home.mp += 1
    away.mp += 1

    home.gf += home_goals
    home.ga += away_goals
    away.gf += away_goals
    away.ga += home_goals

    if home_goals > away_goals:
        home.wins += 1
        home.points += 3
        away.losses += 1
    elif home_goals < away_goals:
        away.wins += 1
        away.points += 3
        home.losses += 1
    else:
        home.draws += 1
        away.draws += 1
        home.points += 1
        away.points += 1


def calculate_standings(league_name: str, season: str) -> tuple[list[StandingRow], str | None]:
    league = find_league(league_name, season)
    if league is None:
        return [], f'Няма лига с име "{normalize_text(league_name)}" сезон {normalize_text(season)}.'

    league_id = int(league["id"])
    teams = [dict(row) for row in standings_repo.get_league_teams(league_id)]
    if not teams:
        return [], f'Няма добавени отбори в лига "{league["name"]}" сезон {league["season"]}.'

    standings = {
        int(team["id"]): StandingRow(club_id=int(team["id"]), team=str(team["name"]))
        for team in teams
    }
    team_ids = set(standings)

    matches = [dict(row) for row in standings_repo.get_league_matches(league_id)]
    invalid_matches = [
        row
        for row in matches
        if int(row["home_club_id"]) not in team_ids or int(row["away_club_id"]) not in team_ids
    ]
    if invalid_matches:
        match_ids = ", ".join(f'#{row["id"]}' for row in invalid_matches)
        return [], (
            "Грешка в данните: има мач с отбор извън league_teams "
            f'за лига "{league["name"]}" сезон {league["season"]}: {match_ids}.'
        )

    for row in matches:
        if row["status"] != "played":
            continue
        if row["home_goals"] is None or row["away_goals"] is None:
            continue

        home = standings[int(row["home_club_id"])]
        away = standings[int(row["away_club_id"])]
        _apply_match(home, away, int(row["home_goals"]), int(row["away_goals"]))

    sorted_rows = sorted(
        standings.values(),
        key=lambda row: (-row.points, -row.gd, -row.gf, row.team.lower()),
    )
    return sorted_rows, None


def format_standings(league_name: str, season: str) -> str:
    league = find_league(league_name, season)
    rows, error = calculate_standings(league_name, season)
    if error is not None:
        return error

    assert league is not None
    lines = [f'Класиране за лига "{league["name"]}" сезон {league["season"]}:']
    if all(row.mp == 0 for row in rows):
        lines.append("Няма изиграни мачове. Таблица с нули:")

    lines.append("Място Отбор MP W D L GF:GA GD PTS")
    for position, row in enumerate(rows, start=1):
        gd = f"+{row.gd}" if row.gd > 0 else str(row.gd)
        lines.append(
            f"{position}. {row.team} {row.mp} {row.wins} {row.draws} {row.losses} "
            f"{row.gf}:{row.ga} {gd} {row.points}"
        )

    return "\n".join(lines)
