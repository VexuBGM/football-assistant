# src/players_service.py
from datetime import datetime
from typing import Optional

from .db import execute, fetch_all, fetch_one

VALID_POSITIONS = {"GK", "DF", "MF", "FW"}
VALID_STATUSES = {"active", "injured", "suspended", "retired"}
POSITION_LABELS = {"GK": "Vr", "DF": "Df", "MF": "Mf", "FW": "Fw"}
STATUS_LABELS = {"active": "active", "injured": "injured", "suspended": "suspended", "retired": "retired"}


def _normalize(text: str) -> str:
    return " ".join(text.strip().split())


def _validate_position(pos: str) -> Optional[str]:
    p = pos.strip().upper()
    if p not in VALID_POSITIONS:
        return None
    return p


def _validate_number(num: int) -> bool:
    return 1 <= num <= 99


def _validate_birth_date(date_str: str) -> Optional[str]:
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _resolve_club(club_identifier: str) -> Optional[dict]:
    ident = club_identifier.strip()
    if ident.isdigit():
        row = fetch_one("SELECT club_id, name FROM Clubs WHERE club_id = ?", (int(ident),))
    else:
        row = fetch_one("SELECT club_id, name FROM Clubs WHERE lower(name) = lower(?)", (_normalize(ident),))
    if row is None:
        return None
    return {"club_id": row["club_id"], "name": row["name"]}


def add_player(full_name: str, club_identifier: str, position: str,
               number: int, birth_date: str, nationality: str) -> str:
    name_n = _normalize(full_name)
    if not name_n:
        return 'Error: player name cannot be empty.'

    club = _resolve_club(club_identifier)
    if club is None:
        return f'No club found: {club_identifier.strip()}. Add it first.'

    pos = _validate_position(position)
    if pos is None:
        return f'Invalid position: {position}. Allowed: GK, DF, MF, FW.'

    if not _validate_number(number):
        return 'Number must be between 1 and 99.'

    bd = _validate_birth_date(birth_date)
    if bd is None:
        return 'Invalid birth date. Format: YYYY-MM-DD, DD.MM.YYYY or DD/MM/YYYY.'

    nat = _normalize(nationality)
    if not nat:
        return 'Error: nationality cannot be empty.'

    dup = fetch_one(
        "SELECT player_id FROM Players WHERE club_id = ? AND number = ?",
        (club["club_id"], number),
    )
    if dup is not None:
        return f'Number {number} is already taken in {club["name"]}.'

    execute(
        "INSERT INTO Players (full_name, birth_date, nationality, position, number, status, club_id) "
        "VALUES (?, ?, ?, ?, ?, 'active', ?)",
        (name_n, bd, nat, pos, number, club["club_id"]),
    )
    return f'Added player: {name_n} - {pos} (#{number}) in {club["name"]}, born {bd}, {nat}'


def list_players(club_identifier: Optional[str] = None) -> str:
    if club_identifier:
        club = _resolve_club(club_identifier)
        if club is None:
            return f'No club found: {club_identifier.strip()}'
        rows = fetch_all(
            "SELECT p.player_id, p.full_name, p.birth_date, p.nationality, "
            "p.position, p.number, p.status, c.name AS club_name "
            "FROM Players p JOIN Clubs c ON p.club_id = c.club_id "
            "WHERE p.club_id = ? ORDER BY p.number ASC",
            (club["club_id"],),
        )
        if not rows:
            return f'No players in {club["name"]}.'
        header = f'Players of {club["name"]}:'
    else:
        rows = fetch_all(
            "SELECT p.player_id, p.full_name, p.birth_date, p.nationality, "
            "p.position, p.number, p.status, c.name AS club_name "
            "FROM Players p JOIN Clubs c ON p.club_id = c.club_id "
            "ORDER BY c.name, p.number ASC",
        )
        if not rows:
            return 'No players found.'
        header = 'All players:'

    lines = [header]
    for r in rows:
        status_txt = f' [{r["status"]}]' if r["status"] != "active" else ""
        lines.append(
            f'  #{r["number"]} {r["full_name"]} - {r["position"]}, '
            f'{r["nationality"]}, born {r["birth_date"]}{status_txt} ({r["club_name"]})'
        )
    return "\n".join(lines)


def update_player(player_name: str, position: Optional[str] = None,
                   number: Optional[int] = None, status: Optional[str] = None) -> str:
    name_n = _normalize(player_name)
    if not name_n:
        return 'Error: must specify player name.'

    player = fetch_one(
        "SELECT p.player_id, p.full_name, p.position, p.number, p.status, p.club_id "
        "FROM Players p WHERE lower(p.full_name) = lower(?)",
        (name_n,),
    )
    if player is None:
        return f'No player found: {name_n}'

    new_pos = player["position"]
    new_num = player["number"]
    new_status = player["status"]

    if position is not None:
        p = _validate_position(position)
        if p is None:
            return f'Invalid position: {position}. Allowed: GK, DF, MF, FW.'
        new_pos = p

    if number is not None:
        if not _validate_number(number):
            return 'Number must be between 1 and 99.'
        dup = fetch_one(
            "SELECT player_id FROM Players WHERE club_id = ? AND number = ? AND player_id != ?",
            (player["club_id"], number, player["player_id"]),
        )
        if dup is not None:
            return f'Number {number} is already taken in this club.'
        new_num = number

    if status is not None:
        s = status.strip().lower()
        if s not in VALID_STATUSES:
            return f'Invalid status. Allowed: active, injured, suspended, retired.'
        new_status = s

    execute(
        "UPDATE Players SET position = ?, number = ?, status = ? WHERE player_id = ?",
        (new_pos, new_num, new_status, player["player_id"]),
    )

    changes = []
    if new_pos != player["position"]:
        changes.append(f'position -> {new_pos}')
    if new_num != player["number"]:
        changes.append(f'number -> #{new_num}')
    if new_status != player["status"]:
        changes.append(f'status -> {new_status}')

    if not changes:
        return f'No changes for {player["full_name"]}.'

    return f'Updated {player["full_name"]}: {", ".join(changes)}'


def delete_player(player_identifier: str) -> str:
    ident = player_identifier.strip()
    if not ident:
        return 'Error: must specify player name or ID.'

    if ident.isdigit():
        pid = int(ident)
        player = fetch_one("SELECT full_name FROM Players WHERE player_id = ?", (pid,))
        if player is None:
            return f'No player with ID {pid}.'
        rc = execute("DELETE FROM Players WHERE player_id = ?", (pid,))
        return f'Deleted player: {player["full_name"]}.' if rc > 0 else 'Delete failed.'
    else:
        name_n = _normalize(ident)
        player = fetch_one("SELECT player_id, full_name FROM Players WHERE lower(full_name) = lower(?)", (name_n,))
        if player is None:
            return f'No player found: {name_n}'
        rc = execute("DELETE FROM Players WHERE player_id = ?", (player["player_id"],))
        return f'Deleted player: {player["full_name"]}.' if rc > 0 else 'Delete failed.'


def seed_test_data() -> str:
    count = fetch_one("SELECT COUNT(*) AS cnt FROM Players")
    if count and count["cnt"] > 0:
        return 'Test data already loaded.'

    test_players = [
        ("Georgi Petkov", "1975-05-10", "Bulgarian", "GK", 1, "active", "Levski Sofia"),
        ("Stefan Velev", "1998-03-22", "Bulgarian", "DF", 4, "active", "Levski Sofia"),
        ("Jose Luis", "1995-11-14", "Spanish", "MF", 8, "active", "Levski Sofia"),
        ("Gustavo Busatto", "1996-01-30", "Brazilian", "FW", 9, "active", "CSKA Sofia"),
        ("Yuri Gali", "1997-07-05", "Brazilian", "MF", 10, "active", "CSKA Sofia"),
        ("Petar Zanev", "1988-12-18", "Bulgarian", "DF", 3, "injured", "CSKA Sofia"),
        ("Simon Slavchev", "1993-09-25", "Bulgarian", "MF", 20, "active", "Ludogorets"),
        ("Claudiu Keseru", "1986-12-02", "Romanian", "FW", 11, "active", "Ludogorets"),
    ]

    added = 0
    for (fname, bdate, nat, pos, num, st, club_name) in test_players:
        club = _resolve_club(club_name)
        if club is None:
            continue
        dup = fetch_one(
            "SELECT player_id FROM Players WHERE club_id = ? AND number = ?",
            (club["club_id"], num),
        )
        if dup is not None:
            continue
        execute(
            "INSERT INTO Players (full_name, birth_date, nationality, position, number, status, club_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (fname, bdate, nat, pos, num, st, club["club_id"]),
        )
        added += 1

    return f'Loaded {added} test players.'
