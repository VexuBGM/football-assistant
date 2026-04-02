# Football Management System (Stage 5)

## Overview

Football chatbot for managing clubs, leagues, players, and transfer history with Python + SQLite. The architecture is split into `chatbot -> router -> services -> repositories -> database`, with regex-based NLU, business validation, round-robin scheduling, and command logging.

## Project structure

```text
sql/schema.sql
src/
  chatbot/
    __init__.py
    intents.json
    nlu.py
    router.py
  repositories/
    leagues_repo.py
  database/
    db.py
  services/
    clubs_service.py
    leagues_service.py
    players_service.py
    transfers_service.py
  utils/
    logger.py
  main.py
tests/
docs/
```

## Main commands

### Clubs

- `add club <name> <city> [year]`
- `list clubs`
- `delete club <name|id>`

### Leagues

- `create league <name> <season>`
- `add team <club> to league <name> <season>`
- `show teams in league <name> <season>`
- `remove team <club> from league <name> <season>`
- `generate schedule <name> <season>`

### Players

- `add player <name> in <club> position <GK|DF|MF|FW> number <1-99> born <date> nat <nationality>`
- `list players`
- `list players of <club>`
- `change number of <player> to <number>`
- `change position of <player> to <position>`
- `change status of <player> to <status>`
- `delete player <name|id>`
- `seed players`

### Transfers

- `transfer <player> from <club> to <club> YYYY-MM-DD [fee <amount>]`
- `show transfers of <player>`
- `show transfers of club <club>`
- `seed transfers`

Bulgarian command variants are supported too, including:

- `Създай лига Първа лига 2025/2026`
- `Добави отбор Левски София в лига Първа лига 2025/2026`
- `Генерирай програма Първа лига 2025/2026`
- `Трансфер Иван Петров от Левски в Лудогорец 2026-03-10`
- `Покажи трансфери на Иван Петров`

## Round-robin schedule

`generate schedule` creates a single round-robin fixture list and stores it in `matches`.

- With an even number of teams, the league gets `N - 1` rounds and `N*(N-1)/2` matches.
- With an odd number of teams, a `BYE` slot is used internally, so the league gets `N` rounds.
- The app refuses to generate a second schedule for the same league unless the old one is removed manually.

## Run

```bash
python -m src.main
```

## Tests

```bash
python -m pytest
```

`pytest.ini` is configured to use a local temp folder so the suite works cleanly in this repo on Windows as well.
