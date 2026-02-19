# Football Clubs Management (ЕТАП 2)

Проект: информационна система (чатбот) за управление на футболни клубове.
Реализира Python ↔ SQLite връзка и CRUD операции за клубове.

## Структура
- `sql/schema.sql` — таблици Clubs/Players/Matches
- `src/db.py` — централизирана DB връзка + заявки
- `src/clubs_service.py` — CRUD за Clubs (валидация + без дубликати)
- `src/chatbot.py` — intent parser (regex) + handler
- `src/main.py` — chat loop + logging към `commands.log`

## Стартиране
1) (По желание) създай виртуална среда
2) Стартирай:
```bash
python -m src.main
