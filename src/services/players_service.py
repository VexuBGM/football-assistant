from datetime import datetime
from typing import Optional

from ..database.db import execute, fetch_all, fetch_one
from .clubs_service import resolve_club

VALID_POSITIONS = {"GK", "DF", "MF", "FW"}
VALID_STATUSES = {"active", "injured", "suspended", "retired"}
FREE_AGENT_LABEL = "Free agent"


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def validate_position(position: str) -> Optional[str]:
    normalized = position.strip().upper()
    if normalized not in VALID_POSITIONS:
        return None
    return normalized


def validate_number(number: int) -> bool:
    return 1 <= number <= 99


def validate_birth_date(date_str: str) -> Optional[str]:
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            parsed = datetime.strptime(date_str.strip(), fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def find_player(player_name: str) -> Optional[dict[str, object]]:
    normalized = normalize_text(player_name)
    if not normalized:
        return None

    row = fetch_one(
        """
        SELECT
          p.id,
          p.full_name,
          p.birth_date,
          p.nationality,
          p.position,
          p.number,
          p.status,
          p.club_id,
          c.name AS club_name
        FROM players p
        LEFT JOIN clubs c ON c.id = p.club_id
        WHERE lower(p.full_name) = lower(?)
        """,
        (normalized,),
    )
    if row is None:
        return None

    return dict(row)


def add_player(
    full_name: str,
    club_identifier: str,
    position: str,
    number: int,
    birth_date: str,
    nationality: str,
) -> str:
    name_n = normalize_text(full_name)
    if not name_n:
        return "Error: player name cannot be empty."

    club = resolve_club(club_identifier)
    if club is None:
        return f"No club found: {club_identifier.strip()}. Add it first."

    valid_position = validate_position(position)
    if valid_position is None:
        return "Invalid position: {}. Allowed: GK, DF, MF, FW.".format(position)

    if not validate_number(number):
        return "Number must be between 1 and 99."

    birth_date_iso = validate_birth_date(birth_date)
    if birth_date_iso is None:
        return "Invalid birth date. Format: YYYY-MM-DD, DD.MM.YYYY or DD/MM/YYYY."

    nationality_n = normalize_text(nationality)
    if not nationality_n:
        return "Error: nationality cannot be empty."

    duplicate = fetch_one(
        "SELECT id FROM players WHERE club_id = ? AND number = ?",
        (club["id"], number),
    )
    if duplicate is not None:
        return f"Number {number} is already taken in {club['name']}."

    execute(
        """
        INSERT INTO players (full_name, birth_date, nationality, position, number, status, club_id)
        VALUES (?, ?, ?, ?, ?, 'active', ?)
        """,
        (name_n, birth_date_iso, nationality_n, valid_position, number, club["id"]),
    )
    return (
        f"Added player: {name_n} - {valid_position} (#{number}) in {club['name']}, "
        f"born {birth_date_iso}, {nationality_n}"
    )


def list_players(club_identifier: Optional[str] = None) -> str:
    if club_identifier:
        club = resolve_club(club_identifier)
        if club is None:
            return f"No club found: {club_identifier.strip()}"
        rows = fetch_all(
            """
            SELECT
              p.id,
              p.full_name,
              p.birth_date,
              p.nationality,
              p.position,
              p.number,
              p.status,
              c.name AS club_name
            FROM players p
            LEFT JOIN clubs c ON c.id = p.club_id
            WHERE p.club_id = ?
            ORDER BY p.number ASC, p.full_name ASC
            """,
            (club["id"],),
        )
        if not rows:
            return f"No players in {club['name']}."
        header = f"Players of {club['name']}:"
    else:
        rows = fetch_all(
            """
            SELECT
              p.id,
              p.full_name,
              p.birth_date,
              p.nationality,
              p.position,
              p.number,
              p.status,
              c.name AS club_name
            FROM players p
            LEFT JOIN clubs c ON c.id = p.club_id
            ORDER BY COALESCE(c.name, 'ZZZ'), p.number ASC, p.full_name ASC
            """
        )
        if not rows:
            return "No players found."
        header = "All players:"

    lines = [header]
    for row in rows:
        status_text = f" [{row['status']}]" if row["status"] != "active" else ""
        club_name = row["club_name"] or FREE_AGENT_LABEL
        lines.append(
            f"  #{row['number']} {row['full_name']} - {row['position']}, "
            f"{row['nationality']}, born {row['birth_date']}{status_text} ({club_name})"
        )
    return "\n".join(lines)


def update_player(
    player_name: str,
    position: Optional[str] = None,
    number: Optional[int] = None,
    status: Optional[str] = None,
) -> str:
    player = find_player(player_name)
    if player is None:
        name_n = normalize_text(player_name)
        if not name_n:
            return "Error: must specify player name."
        return f"No player found: {name_n}"

    new_position = player["position"]
    new_number = player["number"]
    new_status = player["status"]

    if position is not None:
        valid_position = validate_position(position)
        if valid_position is None:
            return f"Invalid position: {position}. Allowed: GK, DF, MF, FW."
        new_position = valid_position

    if number is not None:
        if not validate_number(number):
            return "Number must be between 1 and 99."
        duplicate = fetch_one(
            "SELECT id FROM players WHERE club_id = ? AND number = ? AND id != ?",
            (player["club_id"], number, player["id"]),
        )
        if duplicate is not None:
            return "Number {} is already taken in this club.".format(number)
        new_number = number

    if status is not None:
        normalized_status = status.strip().lower()
        if normalized_status not in VALID_STATUSES:
            return "Invalid status. Allowed: active, injured, suspended, retired."
        new_status = normalized_status

    execute(
        "UPDATE players SET position = ?, number = ?, status = ? WHERE id = ?",
        (new_position, new_number, new_status, player["id"]),
    )

    changes: list[str] = []
    if new_position != player["position"]:
        changes.append(f"position -> {new_position}")
    if new_number != player["number"]:
        changes.append(f"number -> #{new_number}")
    if new_status != player["status"]:
        changes.append(f"status -> {new_status}")

    if not changes:
        return f"No changes for {player['full_name']}."

    return f"Updated {player['full_name']}: {', '.join(changes)}"


def delete_player(player_identifier: str) -> str:
    identifier = normalize_text(player_identifier)
    if not identifier:
        return "Error: must specify player name or ID."

    if identifier.isdigit():
        player = fetch_one("SELECT id, full_name FROM players WHERE id = ?", (int(identifier),))
        if player is None:
            return f"No player with ID {identifier}."
    else:
        player = fetch_one(
            "SELECT id, full_name FROM players WHERE lower(full_name) = lower(?)",
            (identifier,),
        )
        if player is None:
            return f"No player found: {identifier}"

    execute("DELETE FROM players WHERE id = ?", (player["id"],))
    return f"Deleted player: {player['full_name']}."


def seed_test_data() -> str:
    count = fetch_one("SELECT COUNT(*) AS count FROM players")
    if count is not None and count["count"] > 0:
        return "Test data already loaded."

    players = [
        ("Georgi Petkov", "1975-05-10", "Bulgarian", "GK", 1, "active", "Levski Sofia"),
        ("Stefan Velev", "1998-03-22", "Bulgarian", "DF", 4, "active", "Levski Sofia"),
        ("Jose Luis", "1995-11-14", "Spanish", "MF", 8, "active", "Levski Sofia"),
        ("Gustavo Busatto", "1996-01-30", "Brazilian", "FW", 9, "active", "CSKA Sofia"),
        ("Yuri Gali", "1997-07-05", "Brazilian", "MF", 10, "active", "CSKA Sofia"),
        ("Petar Zanev", "1988-12-18", "Bulgarian", "DF", 3, "injured", "CSKA Sofia"),
        ("Claudiu Keseru", "1986-12-02", "Romanian", "FW", 11, "active", "Ludogorets"),
        ("Simon Slavchev", "1993-09-25", "Bulgarian", "MF", 20, "active", "Ludogorets"),
    ]

    added = 0
    for full_name, birth_date, nationality, position, number, status, club_name in players:
        club = resolve_club(club_name)
        if club is None:
            continue
        duplicate = fetch_one(
            "SELECT id FROM players WHERE club_id = ? AND number = ?",
            (club["id"], number),
        )
        if duplicate is not None:
            continue
        execute(
            """
            INSERT INTO players (full_name, birth_date, nationality, position, number, status, club_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (full_name, birth_date, nationality, position, number, status, club["id"]),
        )
        added += 1

    return f"Loaded {added} test players."
