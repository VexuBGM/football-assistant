# Football Management System

A staged school project for managing football clubs, players, leagues, transfers, matches, standings, and rule-based match predictions.

The project has two interfaces:

- A command-line chatbot: `python -m src.main`
- A local browser UI built with NiceGUI: `python -m src.ui.app`

Both interfaces use the same service layer and SQLite database, so validation and business rules stay consistent.

## Quickstart From Scratch

These commands assume a fresh clone on Windows PowerShell.

```powershell
git clone <repository-url>
cd futbul
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest
python -m src.main
```

If PowerShell blocks virtual environment activation, run this in the same terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

To run the browser app:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.ui.app
```

Open this address in a browser:

```text
http://127.0.0.1:8080
```

## Requirements

- Python 3.13 was used for verification
- SQLite, included with Python through the `sqlite3` module
- Python packages from [requirements.txt](requirements.txt):
  - `nicegui`
  - `pytest`

## Clean Local Reset

The app creates `football_clubs.db` automatically from [sql/schema.sql](sql/schema.sql). If the database was created with an older schema, delete it and start again:

```powershell
Remove-Item .\football_clubs.db -ErrorAction SilentlyContinue
python -m src.main
```

This removes only the generated local database file. Source code and documentation are not affected.

## Project Structure

```text
futbul/
  README.md
  requirements.txt
  pytest.ini
  manual_stage_verification.py
  sql/
    schema.sql
  docs/
    stages/
    scenarios/
    nicegui_ui_plan.md
  src/
    main.py
    db.py
    chatbot/
      __init__.py
      intents.json
      models.py
      nlu.py
      router.py
    database/
      db.py
    services/
      clubs_service.py
      players_service.py
      transfers_service.py
      leagues_service.py
      matches_service.py
      standings_service.py
    repositories/
      ai_repo.py
      leagues_repo.py
      matches_repo.py
      standings_repo.py
    ai/
      ai_service.py
      features.py
    ui/
      app.py
      adapters.py
      layout.py
      notifications.py
      pages/
    utils/
      logger.py
  tests/
```

## How The Application Works

The main architecture is:

```text
chatbot / NiceGUI UI
        -> services
        -> repositories
        -> database
        -> SQLite
```

The command-line chatbot works like this:

1. `src.main` initializes the database.
2. `src.chatbot.nlu.RegexNLU` matches the user text against regex patterns in `src/chatbot/intents.json`.
3. `src.chatbot.router.ChatbotRouter` chooses the correct service function.
4. Service modules validate the business rules.
5. Repository and database modules read or write SQLite data.
6. Commands and responses are logged to `commands.log`.

The NiceGUI app works like this:

1. `src.ui.app` initializes the database and starts a local web server.
2. Page modules in `src/ui/pages/` render the browser screens.
3. UI actions call the same service functions used by the chatbot.
4. Validation errors are shown in the UI and logged when relevant.

## Database

The SQLite schema is stored in [sql/schema.sql](sql/schema.sql). It creates these main tables:

- `clubs`: club name, city, founded year
- `players`: player details, position, squad number, status, current club
- `transfers`: transfer history with date, fee, source club, target club
- `leagues`: league name and season
- `league_teams`: clubs registered in a league
- `matches`: generated fixtures and saved results
- `goals`: match goal events
- `cards`: match card events

Important rules enforced by code and schema:

- Club names are unique.
- Player positions must be `GK`, `DF`, `MF`, or `FW`.
- Player numbers must be from 1 to 99 and unique inside the same club.
- Match event minutes must be from 1 to 120.
- A match cannot have the same home and away club.
- Transfers cannot move a player to the same club.
- Standings are calculated from played matches only; points are never entered manually.

## Main Chatbot Commands

Start the chatbot:

```powershell
python -m src.main
```

Then type commands at the `>` prompt.

### General

```text
help
exit
```

### Clubs

```text
add club <name> <city> [year]
list clubs
delete club <name|id>
```

Examples:

```text
add club Levski Sofia 1914
add club CSKA Sofia 1948
list clubs
```

### Players

```text
add player <name> in <club> position <GK|DF|MF|FW> number <1-99> born <YYYY-MM-DD> nat <nationality>
list players
list players of <club>
change number of <player> to <number>
change position of <player> to <GK|DF|MF|FW>
change status of <player> to <active|injured|suspended|retired>
delete player <name|id>
seed players
```

Examples:

```text
add player Ivan Petrov in Levski position FW number 9 born 2001-04-12 nat Bulgaria
list players of Levski
change status of Ivan Petrov to injured
```

### Transfers

```text
transfer <player> from <club> to <club> YYYY-MM-DD [fee <amount>]
transfer <player> to <club> YYYY-MM-DD [fee <amount>]
show transfers of <player>
show transfers of player <player>
show transfers of club <club>
seed transfers
```

Examples:

```text
transfer Ivan Petrov from Levski to CSKA 2026-03-10 fee 1200000
show transfers of Ivan Petrov
show transfers of club CSKA
```

### Leagues

```text
create league <name> <season>
add team <club> to league <name> <season>
show teams in league <name> <season>
remove team <club> from league <name> <season>
generate schedule <name> <season>
```

Examples:

```text
create league First League 2025/2026
add team Levski to league First League 2025/2026
add team CSKA to league First League 2025/2026
generate schedule First League 2025/2026
```

### Matches

```text
select league <name> <season>
show round <number> <league> <season>
select match <match_id>
result <home>-<away> <home_goals>:<away_goals> save
goal <player> <club> <minute>
card <player> <club> <Y|R> <minute>
show events [match_id]
```

Normal match workflow:

```text
select league First League 2025/2026
show round 1 First League 2025/2026
select match 1
result Levski-CSKA 2:1 save
goal Ivan Petrov Levski 23
card Georgi Ivanov CSKA Y 55
show events
```

### Standings

```text
show standings <league> <season>
```

Example:

```text
show standings First League 2025/2026
```

Standings include every team registered in the league. Only matches with `status = 'played'` and saved scores are counted.

Sorting order:

1. Points
2. Goal difference
3. Goals for
4. Team name

### AI Match Prediction

```text
prediction <home team> vs <away team>
predict <home team> vs <away team>
```

Example:

```text
prediction Levski vs CSKA
```

The prediction module is rule-based. It uses real database data from played matches:

- recent form from the last 5 matches
- average goals scored
- average goals conceded
- calculated standings position
- home advantage

Output probabilities always sum to 100%:

- home win
- draw
- away win

## Browser UI

Start the visual dashboard:

```powershell
python -m src.ui.app
```

Then open:

```text
http://127.0.0.1:8080
```

The UI includes:

- Dashboard with database counts and recent results
- Dashboard button to seed full demo data for quick testing
- Dashboard button to clear all database rows while keeping the schema
- Club management
- Player management
- League team management
- Schedule generation
- Match Center for result entry, goals, cards, and event review
- Calculated standings
- Transfer history
- AI prediction
- Chatbot page for command demonstrations

For quick manual testing, open the Dashboard and click **Seed Full Demo Data**. It creates clubs, squads, transfer history, two leagues, played results, scheduled sandbox fixtures, goals, and cards. Use **Clear Database** on the Dashboard when you want to remove all saved rows and start again without deleting `football_clubs.db`. Use `Seeded Premier League 2025/2026` for standings and AI prediction demos, and `Seeded Match Sandbox 2026/2027` for saving new results in Match Center. The sandbox league has 6 teams, 5 rounds, and 15 scheduled matches, so each round shows 3 fixtures.

## Logging

Chatbot commands and UI actions are written to:

```text
commands.log
```

The log stores command text, parsed intent, entities, response, and timestamp. This helps demonstrate the required command processing and testing evidence for the school project.

## Testing

Run the full automated test suite:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest
```

The repository includes tests for:

- club CRUD
- player CRUD and validation
- transfer rules and history
- league team management
- schedule generation
- match result and event validation
- standings calculation
- AI prediction
- chatbot command routing
- command logging

There is also a manual verification helper:

```powershell
python manual_stage_verification.py
```

## Documentation Artifacts

Teacher stage requirements are stored in:

```text
docs/stages/
```

Project scenarios and example dialogs are stored in:

```text
docs/scenarios/
```

Important scenario files:

- [docs/scenarios/example_dialog_stage3.md](docs/scenarios/example_dialog_stage3.md)
- [docs/scenarios/example_dialog_stage4.md](docs/scenarios/example_dialog_stage4.md)
- [docs/scenarios/example_dialog_stage5.md](docs/scenarios/example_dialog_stage5.md)
- [docs/scenarios/example_dialog_stage6.md](docs/scenarios/example_dialog_stage6.md)
- [docs/scenarios/example_dialog_stage7.md](docs/scenarios/example_dialog_stage7.md)
- [docs/scenarios/example_dialog_stage8.md](docs/scenarios/example_dialog_stage8.md)
- [docs/scenarios/stage4_test_scenarios.md](docs/scenarios/stage4_test_scenarios.md)
- [docs/scenarios/stage5_test_scenarios.md](docs/scenarios/stage5_test_scenarios.md)
- [docs/scenarios/stage6_test_scenarios.md](docs/scenarios/stage6_test_scenarios.md)
- [docs/scenarios/stage7_test_scenarios.md](docs/scenarios/stage7_test_scenarios.md)
- [docs/scenarios/stage8_test_scenarios.md](docs/scenarios/stage8_test_scenarios.md)
- [docs/scenarios/stage8_ai_model.md](docs/scenarios/stage8_ai_model.md)

## Feature Summary By Stage

### Stage 1: Analysis, Design, Database

- Project description and core functions
- Main entities
- SQLite database choice
- SQL schema
- Test data support

### Stage 2: Python, SQL, Clubs CRUD

- Python to SQLite connection
- Club create, list, and delete
- Basic chatbot loop
- Regex command parsing
- Command logging

### Stage 3: Players

- Players linked to clubs
- Player CRUD
- Validation for position, number, birth date, and status
- Filtering by club

### Stage 4: Transfers

- Transfer history table
- Atomic transfer operation
- Transfer validation rules
- Player and club transfer history commands

### Stage 5: Leagues

- League creation
- Team registration in leagues
- Round-robin schedule generation
- Duplicate schedule prevention

### Stage 6: Matches

- League and match selection context
- Result entry
- Goals and cards
- Event review
- Validation for player, team, and minute logic

### Stage 7: Standings

- Standings calculated from played matches
- No manual points entry
- Sorting by points, goal difference, goals for, and team name
- Edge case validation for scheduled matches and invalid data

### Stage 8: AI Prediction

- Match prediction command
- Home win, draw, and away win probabilities
- Rule-based model using real database data
- Documented model logic and limitations

## Troubleshooting

### `ModuleNotFoundError: No module named 'nicegui'`

Install dependencies inside the active virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### `Could not open requirements file`

Make sure the terminal is in the project root, where `requirements.txt` exists:

```powershell
cd C:\Users\Students\Downloads\futbul
```

For a fresh clone, use the folder created by `git clone`.

### `no such column` or old database errors

Delete the generated SQLite file and run the app again:

```powershell
Remove-Item .\football_clubs.db -ErrorAction SilentlyContinue
python -m src.main
```

### Port 8080 already in use

Stop the other process using port 8080, or change the `port` value in [src/ui/app.py](src/ui/app.py).

## Recommended Demo Flow

Use this short flow to demonstrate the project after a clean database reset:

```text
add club Levski Sofia 1914
add club CSKA Sofia 1948
add club Ludogorets Razgrad 2001
add club Botev Plovdiv 1912
create league First League 2025/2026
add team Levski to league First League 2025/2026
add team CSKA to league First League 2025/2026
add team Ludogorets to league First League 2025/2026
add team Botev to league First League 2025/2026
add player Ivan Petrov in Levski position FW number 9 born 2001-04-12 nat Bulgarian
add player Georgi Ivanov in CSKA position DF number 5 born 1999-08-20 nat Bulgarian
generate schedule First League 2025/2026
show round 1 First League 2025/2026
select league First League 2025/2026
select match 2
result CSKA-Levski 1:2 save
goal Ivan Petrov Levski 23
card Georgi Ivanov CSKA Y 55
show events
show standings First League 2025/2026
```

For AI prediction, the model needs enough played match history. Use the Stage 8 scenarios in [docs/scenarios/stage8_test_scenarios.md](docs/scenarios/stage8_test_scenarios.md) when demonstrating that module.
