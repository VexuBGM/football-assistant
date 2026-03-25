from typing import Optional

from ..database.db import execute, fetch_all, fetch_one


def _normalize_name(name: str) -> str:
    return " ".join(name.strip().split())


def resolve_club(club_identifier: str) -> Optional[dict[str, object]]:
    identifier = _normalize_name(club_identifier)
    if not identifier:
        return None

    if identifier.isdigit():
        row = fetch_one("SELECT id, name, city, founded_year FROM clubs WHERE id = ?", (int(identifier),))
    else:
        row = fetch_one(
            "SELECT id, name, city, founded_year FROM clubs WHERE lower(name) = lower(?)",
            (identifier,),
        )

    if row is None:
        return None

    return {
        "id": row["id"],
        "name": row["name"],
        "city": row["city"],
        "founded_year": row["founded_year"],
    }


def add_club(name: str, city: str, founded_year: Optional[int] = None) -> str:
    name_n = _normalize_name(name)
    city_n = _normalize_name(city)

    if not name_n:
        return "Error: club name cannot be empty."
    if not city_n:
        return "Error: club city cannot be empty."

    existing = resolve_club(name_n)
    if existing is not None:
        return f'Club with name "{name_n}" already exists.'

    execute(
        "INSERT INTO clubs (name, city, founded_year) VALUES (?, ?, ?)",
        (name_n, city_n, founded_year),
    )
    founded_text = f", founded {founded_year}" if founded_year is not None else ""
    return f"Added club: {name_n} ({city_n}{founded_text})"


def get_all_clubs() -> str:
    rows = fetch_all("SELECT id, name, city, founded_year FROM clubs ORDER BY name ASC")
    if not rows:
        return "No clubs found."

    lines = ["Clubs:"]
    for row in rows:
        founded_text = f", founded {row['founded_year']}" if row["founded_year"] is not None else ""
        lines.append(f"- [{row['id']}] {row['name']} - {row['city']}{founded_text}")
    return "\n".join(lines)


def delete_club(club_identifier: str) -> str:
    identifier = _normalize_name(club_identifier)
    if not identifier:
        return "Error: must specify club name or ID."

    club = resolve_club(identifier)
    if club is None:
        if identifier.isdigit():
            return f"No club with ID {identifier}."
        return f'No club with name "{identifier}".'

    try:
        execute("DELETE FROM clubs WHERE id = ?", (club["id"],))
    except RuntimeError as exc:
        return f"Cannot delete club {club['name']}: {exc}"

    return f"Deleted club: {club['name']}."


def update_club(
    club_id: int,
    name: Optional[str] = None,
    city: Optional[str] = None,
    founded_year: Optional[int] = None,
) -> str:
    row = fetch_one("SELECT id, name, city, founded_year FROM clubs WHERE id = ?", (club_id,))
    if row is None:
        return f"No club with ID {club_id}."

    new_name = _normalize_name(name) if name is not None else row["name"]
    new_city = _normalize_name(city) if city is not None else row["city"]
    new_year = founded_year if founded_year is not None else row["founded_year"]

    if not new_name:
        return "Error: club name cannot be empty."
    if not new_city:
        return "Error: club city cannot be empty."

    duplicate = fetch_one(
        "SELECT id FROM clubs WHERE lower(name) = lower(?) AND id != ?",
        (new_name, club_id),
    )
    if duplicate is not None:
        return f'Cannot update: another club with name "{new_name}" already exists.'

    execute(
        "UPDATE clubs SET name = ?, city = ?, founded_year = ? WHERE id = ?",
        (new_name, new_city, new_year, club_id),
    )
    return f"Updated club [{club_id}]: {new_name} - {new_city}"
