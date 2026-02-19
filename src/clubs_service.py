# src/clubs_service.py
from typing import Optional

from .db import execute, fetch_all, fetch_one


def _normalize_name(name: str) -> str:
    return " ".join(name.strip().split())


def add_club(name: str, city: str, founded_year: Optional[int] = None) -> str:
    name_n = _normalize_name(name)
    city_n = " ".join(city.strip().split())

    if not name_n:
        return "❌ Грешка: името на клуба не може да е празно."
    if not city_n:
        return "❌ Грешка: градът не може да е празен."

    existing = fetch_one("SELECT club_id FROM Clubs WHERE lower(name) = lower(?)", (name_n,))
    if existing is not None:
        return f"⚠️ Клуб с име „{name_n}“ вече съществува."

    execute(
        "INSERT INTO Clubs (name, city, founded_year) VALUES (?, ?, ?)",
        (name_n, city_n, founded_year),
    )
    return f"✅ Добавен клуб: {name_n} ({city_n})"


def get_all_clubs() -> str:
    rows = fetch_all("SELECT club_id, name, city, founded_year FROM Clubs ORDER BY name ASC")
    if not rows:
        return "ℹ️ Няма записани клубове."

    lines = ["📋 Клубове:"]
    for r in rows:
        fy = r["founded_year"]
        fy_txt = f", основан {fy} г." if fy is not None else ""
        lines.append(f"- [{r['club_id']}] {r['name']} — {r['city']}{fy_txt}")
    return "\n".join(lines)


def delete_club(club_identifier: str) -> str:
    """
    Позволява изтриване по ID (ако е число) или по име.
    """
    ident = club_identifier.strip()
    if not ident:
        return "❌ Грешка: трябва да подадеш име или ID."

    if ident.isdigit():
        club_id = int(ident)
        existing = fetch_one("SELECT name FROM Clubs WHERE club_id = ?", (club_id,))
        if existing is None:
            return f"❌ Няма клуб с ID {club_id}."
        rc = execute("DELETE FROM Clubs WHERE club_id = ?", (club_id,))
        return f"✅ Изтрит клуб [{club_id}] {existing['name']}." if rc > 0 else "❌ Неуспешно изтриване."
    else:
        name_n = _normalize_name(ident)
        existing = fetch_one("SELECT club_id FROM Clubs WHERE lower(name) = lower(?)", (name_n,))
        if existing is None:
            return f"❌ Няма клуб с име „{name_n}“."
        rc = execute("DELETE FROM Clubs WHERE lower(name) = lower(?)", (name_n,))
        return f"✅ Изтрит клуб: {name_n}." if rc > 0 else "❌ Неуспешно изтриване."


def update_club(club_id: int, name: Optional[str] = None, city: Optional[str] = None, founded_year: Optional[int] = None) -> str:
    existing = fetch_one("SELECT club_id, name, city, founded_year FROM Clubs WHERE club_id = ?", (club_id,))
    if existing is None:
        return f"❌ Няма клуб с ID {club_id}."

    new_name = _normalize_name(name) if name is not None else existing["name"]
    new_city = " ".join(city.strip().split()) if city is not None else existing["city"]
    new_year = founded_year if founded_year is not None else existing["founded_year"]

    if not new_name:
        return "❌ Грешка: името не може да е празно."
    if not new_city:
        return "❌ Грешка: градът не може да е празен."

    dup = fetch_one(
        "SELECT club_id FROM Clubs WHERE lower(name) = lower(?) AND club_id != ?",
        (new_name, club_id),
    )
    if dup is not None:
        return f"⚠️ Не може: вече има друг клуб с име „{new_name}“."

    execute(
        "UPDATE Clubs SET name = ?, city = ?, founded_year = ? WHERE club_id = ?",
        (new_name, new_city, new_year, club_id),
    )
    return f"✅ Обновен клуб [{club_id}]: {new_name} — {new_city}"
