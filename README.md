# Football Management System (Stage 4)

## Overview

Football chatbot for managing clubs, players, and transfer history with Python + SQLite. The architecture is now split into `chatbot -> router -> services -> database`, with regex-based NLU, business validation, and command logging.

## Project structure

```text
sql/schema.sql
src/
  chatbot/
    __init__.py
    intents.json
    nlu.py
    router.py
  database/
    db.py
  services/
    clubs_service.py
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

- `Трансфер Иван Петров от Левски в Лудогорец 2026-03-10`
- `Покажи трансфери на Иван Петров`
- `Покажи трансфери на Левски`

## Run

```bash
python -m src.main
```

## Tests

```bash
python -m pytest
```

`pytest.ini` is configured to use a local temp folder so the suite works cleanly in this repo on Windows as well.
