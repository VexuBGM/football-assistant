# Football Management System (Stage 7)

## Overview

Football chatbot for managing clubs, leagues, players, transfer history, match operations, and league standings with Python + SQLite. The architecture is split into `chatbot -> router -> services -> repositories -> database`, with regex-based NLU, business validation, round-robin scheduling, match context selection, event tracking, standings calculated from played matches, and command logging.

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
    matches_repo.py
    standings_repo.py
  database/
    db.py
  services/
    clubs_service.py
    leagues_service.py
    matches_service.py
    standings_service.py
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

### Matches

- `select league <name> <season>`
- `show round <number> <league> <season>`
- `select match <match_id>`
- `result <home>-<away> <X>:<Y> save`
- `goal <player> <club> <minute>`
- `card <player> <club> <Y|R> <minute>`
- `show events [match_id]`

### Standings

- `show standings <league> <season>`
- `Покажи класиране <лига> <сезон>`

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
- `Избери лига Първа лига 2025/2026`
- `Покажи кръг 1 Първа лига 2025/2026`
- `Избери мач 1`
- `Резултат Левски-ЦСКА 2:1 запиши`
- `Гол Иван Петров Левски 23 минута`
- `Картон Петър Димитров ЦСКА Y 55`
- `Покажи събития`
- `Покажи класиране Първа лига 2025/2026`
- `Трансфер Иван Петров от Левски в Лудогорец 2026-03-10`
- `Покажи трансфери на Иван Петров`

## Round-robin schedule

`generate schedule` creates a single round-robin fixture list and stores it in `matches`.

- With an even number of teams, the league gets `N - 1` rounds and `N*(N-1)/2` matches.
- With an odd number of teams, a `BYE` slot is used internally, so the league gets `N` rounds.
- The app refuses to generate a second schedule for the same league unless the old one is removed manually.

## Match workflow

Stage 6 uses the teacher-recommended context flow:

1. Select a league with `select league <name> <season>`.
2. Inspect a round with `show round <number> <league> <season>`.
3. Select a concrete match with `select match <match_id>`.
4. Save the result, then add goals and cards, and review them with `show events`.

The project uses the simpler Stage 6 consistency mode: the saved result is the primary record, and goals/cards are stored as match statistics. A match result can only be saved once through the chatbot unless a separate edit command is added later.

## Standings workflow

Stage 7 calculates standings directly from `matches`; points and positions are never entered manually.

- Only matches with `status = 'played'` and a saved score are counted.
- A scheduled match with score data is ignored by standings; the normal `result ... save` command sets the status to `played`.
- Every team in `league_teams` appears in the table, including teams with zero played matches.
- Sorting is by points, goal difference, goals for, then team name.
- If a match references a team outside `league_teams` for that league, the standings command returns a data consistency error.

Output columns: position, team, MP, W, D, L, GF:GA, GD, PTS.

## Run

```bash
python -m src.main
```

## Tests

```bash
python -m pytest
```

`pytest.ini` is configured to use a local temp folder so the suite works cleanly in this repo on Windows as well.
