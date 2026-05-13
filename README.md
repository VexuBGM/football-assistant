# Football Management System (Stage 8)

## Overview

Football chatbot for managing clubs, leagues, players, transfer history, match operations, league standings, and AI match predictions with Python + SQLite. The architecture is split into `chatbot -> router -> services/ai -> repositories -> database`, with regex-based NLU, business validation, round-robin scheduling, match context selection, event tracking, standings calculated from played matches, rule-based predictions from real match data, and command logging.

## Project structure

```text
sql/schema.sql
src/
  ai/
    ai_service.py
    features.py
  chatbot/
    __init__.py
    intents.json
    nlu.py
    router.py
  repositories/
    ai_repo.py
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

### AI Prediction

- `prediction <home team> vs <away team>`
- `predict <home team> vs <away team>`
- `Прогноза <отбор1> срещу <отбор2>`

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
- `Прогноза Левски срещу Лудогорец`
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

## AI prediction workflow

Stage 8 adds a rule-based AI module:

- The command is `prediction <home team> vs <away team>` or `Прогноза <отбор1> срещу <отбор2>`.
- Both clubs must exist and must share at least one league.
- The module uses only played matches with saved results.
- Each team needs at least 5 played matches in the selected common league.
- Features: last-5 form, average GF/GA, current calculated standings position, and home advantage.
- Output: home win, draw, away win probabilities. The percentages are never negative and sum to 100%.

Detailed documentation:

- `docs/stage8_ai_model.md`
- `docs/example_dialog_stage8.md`
- `docs/stage8_test_scenarios.md`

## Setup and run

Run all commands from the project root:

```powershell
cd C:\footballgpt
```

If you use the included virtual environment, activate it first:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, allow it for the current terminal session and try again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

The app uses SQLite and creates `football_clubs.db` automatically from `sql/schema.sql`.
If you already have an old local database and see an error like `no such column: status`,
reset the local database before running the app:

```powershell
Remove-Item .\football_clubs.db
```

This deletes only the local generated database file. The next command recreates it with the
current schema:

```powershell
python -m src.main
```

When the app starts, type commands at the `>` prompt. Useful first commands:

```text
help
list clubs
exit
```

The chatbot writes command history to `commands.log`.

## Full clean run checklist

Use this when starting from a fresh download or after pulling stage changes:

```powershell
cd C:\footballgpt
.\venv\Scripts\Activate.ps1
Remove-Item .\football_clubs.db -ErrorAction SilentlyContinue
python -m src.main
```

## Tests

```powershell
cd C:\footballgpt
.\venv\Scripts\Activate.ps1
python -m pytest
```

`pytest.ini` is configured to use a local temp folder so the suite works cleanly in this repo on Windows as well.
