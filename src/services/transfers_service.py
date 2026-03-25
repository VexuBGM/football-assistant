from datetime import datetime
from typing import Optional

from ..database.db import fetch_all, fetch_one, transaction
from .clubs_service import add_club, resolve_club
from .players_service import FREE_AGENT_LABEL, add_player, find_player, normalize_text

FREE_AGENT_TOKENS = {
    "",
    "free",
    "free agent",
    "none",
    "no club",
    "няма",
    "свободен",
    "свободен агент",
}


def _is_free_agent_token(value: Optional[str]) -> bool:
    if value is None:
        return True
    return normalize_text(value).lower() in FREE_AGENT_TOKENS


def _validate_transfer_date(date_str: str) -> bool:
    try:
        parsed = datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except ValueError:
        return False
    return parsed.strftime("%Y-%m-%d") == date_str.strip()


def _normalize_fee(fee: Optional[object]) -> tuple[Optional[float], Optional[str]]:
    if fee is None or fee == "":
        return None, None

    raw = str(fee).strip().replace(",", ".")
    try:
        parsed = float(raw)
    except ValueError:
        return None, "Fee must be a number greater than or equal to 0."

    if parsed < 0:
        return None, "Fee must be a number greater than or equal to 0."

    return parsed, None


def transfer_player(
    player_name: str,
    from_club: Optional[str],
    to_club: str,
    date: str,
    fee: Optional[object] = None,
) -> str:
    name_n = normalize_text(player_name)
    if not name_n:
        return "Error: player name cannot be empty."

    if not _validate_transfer_date(date):
        return "Invalid transfer date. Format: YYYY-MM-DD."

    fee_value, fee_error = _normalize_fee(fee)
    if fee_error is not None:
        return fee_error

    player = find_player(name_n)
    if player is None:
        return f"No player found: {name_n}"

    destination = resolve_club(to_club)
    if destination is None:
        return f"No club found: {normalize_text(to_club)}"

    source = None
    if not _is_free_agent_token(from_club):
        source = resolve_club(from_club or "")
        if source is None:
            return f"No club found: {normalize_text(from_club or '')}"

    if source is not None and source["id"] == destination["id"]:
        return "Transfer failed: source and destination clubs must be different."

    current_club_id = player["club_id"]
    current_club_name = player["club_name"]

    if current_club_id is None:
        if source is not None:
            return (
                f"Transfer failed: {player['full_name']} is currently without a club. "
                'Use "free agent" or leave the source club empty.'
            )
        from_club_id = None
        from_label = FREE_AGENT_LABEL
    else:
        if source is None:
            return (
                f"Transfer failed: {player['full_name']} currently belongs to {current_club_name}. "
                'The "from" club must match the current club.'
            )
        if current_club_id != source["id"]:
            return (
                f"Transfer failed: {player['full_name']} currently belongs to "
                f"{current_club_name}, not {source['name']}."
            )
        from_club_id = source["id"]
        from_label = source["name"]

    try:
        with transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee)
                VALUES (?, ?, ?, ?, ?)
                """,
                (player["id"], from_club_id, destination["id"], date, fee_value),
            )
            cursor.execute(
                "UPDATE players SET club_id = ? WHERE id = ?",
                (destination["id"], player["id"]),
            )
    except RuntimeError as exc:
        return f"Transfer failed: {exc}"

    fee_text = ""
    if fee_value is not None:
        fee_text = f" Fee: {fee_value:g}."

    return (
        f"Transfer completed: {player['full_name']} from {from_label} "
        f"to {destination['name']} on {date}.{fee_text}"
    )


def list_transfers_by_player(player_name: str) -> str:
    name_n = normalize_text(player_name)
    if not name_n:
        return "Error: player name cannot be empty."

    player = find_player(name_n)
    if player is None:
        return f"No player found: {name_n}"

    rows = fetch_all(
        """
        SELECT
          t.transfer_date,
          t.fee,
          from_club.name AS from_club_name,
          to_club.name AS to_club_name
        FROM transfers t
        LEFT JOIN clubs from_club ON from_club.id = t.from_club_id
        JOIN clubs to_club ON to_club.id = t.to_club_id
        WHERE t.player_id = ?
        ORDER BY t.transfer_date DESC, t.id DESC
        """,
        (player["id"],),
    )
    if not rows:
        return f"No transfers found for {player['full_name']}."

    lines = [f"Transfers for {player['full_name']}:"]
    for row in rows:
        from_name = row["from_club_name"] or FREE_AGENT_LABEL
        fee_text = f" | fee {row['fee']:g}" if row["fee"] is not None else ""
        lines.append(f"- {row['transfer_date']}: {from_name} -> {row['to_club_name']}{fee_text}")
    return "\n".join(lines)


def list_transfers_by_club(club_name: str) -> str:
    club = resolve_club(club_name)
    if club is None:
        return f"No club found: {normalize_text(club_name)}"

    rows = fetch_all(
        """
        SELECT
          t.transfer_date,
          t.fee,
          p.full_name,
          from_club.name AS from_club_name,
          to_club.name AS to_club_name
        FROM transfers t
        JOIN players p ON p.id = t.player_id
        LEFT JOIN clubs from_club ON from_club.id = t.from_club_id
        JOIN clubs to_club ON to_club.id = t.to_club_id
        WHERE t.from_club_id = ? OR t.to_club_id = ?
        ORDER BY t.transfer_date DESC, t.id DESC
        """,
        (club["id"], club["id"]),
    )
    if not rows:
        return f"No transfers found for {club['name']}."

    lines = [f"Transfers for club {club['name']}:"]
    for row in rows:
        direction = "IN" if row["to_club_name"] == club["name"] else "OUT"
        from_name = row["from_club_name"] or FREE_AGENT_LABEL
        fee_text = f" | fee {row['fee']:g}" if row["fee"] is not None else ""
        lines.append(
            f"- {row['transfer_date']} [{direction}] {row['full_name']}: "
            f"{from_name} -> {row['to_club_name']}{fee_text}"
        )
    return "\n".join(lines)


def seed_transfer_history() -> str:
    existing = fetch_one("SELECT COUNT(*) AS count FROM transfers")
    if existing is not None and existing["count"] > 0:
        return "Transfer test history already loaded."

    clubs = [
        ("Levski Sofia", "Sofia", 1914),
        ("CSKA Sofia", "Sofia", 1948),
        ("Ludogorets", "Razgrad", 2001),
        ("Botev Plovdiv", "Plovdiv", 1912),
    ]
    for name, city, founded_year in clubs:
        add_club(name, city, founded_year)

    players = [
        ("Ivan Petrov", "Levski Sofia", "MF", 8, "1999-09-09", "Bulgarian"),
        ("Martin Dimitrov", "CSKA Sofia", "DF", 5, "1998-06-11", "Bulgarian"),
        ("Nikolay Georgiev", "Botev Plovdiv", "FW", 11, "2000-01-02", "Bulgarian"),
        ("Petar Kolev", "Ludogorets", "GK", 1, "1997-04-14", "Bulgarian"),
        ("Daniel Ivanov", "Levski Sofia", "FW", 9, "1996-08-23", "Bulgarian"),
        ("Asen Todorov", "CSKA Sofia", "MF", 7, "2001-03-19", "Bulgarian"),
    ]
    for full_name, club_name, position, number, birth_date, nationality in players:
        if find_player(full_name) is None:
            add_player(full_name, club_name, position, number, birth_date, nationality)

    transfers = [
        ("Ivan Petrov", "Levski Sofia", "Ludogorets", "2025-01-10", 50000),
        ("Ivan Petrov", "Ludogorets", "CSKA Sofia", "2025-08-01", 75000),
        ("Martin Dimitrov", "CSKA Sofia", "Botev Plovdiv", "2025-07-15", 20000),
        ("Nikolay Georgiev", "Botev Plovdiv", "Levski Sofia", "2025-09-01", 30000),
        ("Daniel Ivanov", "Levski Sofia", "CSKA Sofia", "2026-01-20", 120000),
    ]
    completed = 0
    for player_name, from_club, to_club, date, fee in transfers:
        result = transfer_player(player_name, from_club, to_club, date, fee)
        if result.startswith("Transfer completed:"):
            completed += 1

    return f"Loaded {completed} test transfers."
