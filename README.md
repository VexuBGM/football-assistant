# Football Management System (Stage 3)

## Описание на проекта
Информационна система (чатбот) за управление на футболни клубове и играчи. Реализира Python + SQLite връзка и CRUD операции за клубове и играчи. Системата е изградена с regex-базиран NLP парсер, валидация на данни и поддръжка на български и английски команди.

## Структура
```
sql/schema.sql          — таблици Clubs, Players, Matches
src/
  db.py                 — централизирана DB връзка + заявки
  clubs_service.py      — CRUD за Clubs (валидация + без дубликати)
  players_service.py    — CRUD за Players (валидация, филтри по клуб)
  chatbot.py            — intent parser (regex) + handler
  intents.json          — regex шаблони за всички команди (BG + EN)
  main.py               — chat loop + logging към commands.log
tests/
  conftest.py           — pytest fixture (изолирана in-memory DB)
  test_clubs_service.py — 21 теста за clubs_service
  test_players_service.py — 52 теста за players_service
  test_chatbot.py       — 43 теста за chatbot (parse + handle)
docs/
  example_dialog_stage3.md — примерен диалог (16 реплики)
```

## Функционалност

### Клубове
| Команда | Описание |
|---|---|
| `add club <име> <град> [година]` | Добавяне на клуб |
| `list clubs` | Списък на всички клубове |
| `delete club <име\|id>` | Изтриване на клуб |

### Играчи
| Команда | Описание |
|---|---|
| `add player <име> in <клуб> position <GK\|DF\|MF\|FW> number <1-99> born <дата> nat <нац>` | Добавяне на играч |
| `list players of <клуб>` | Играчи на конкретен клуб |
| `list players` | Всички играчи |
| `change number of <играч> to <номер>` | Смяна на номер |
| `change position of <играч> to <позиция>` | Смяна на позиция |
| `change status of <играч> to <статус>` | Смяна на статус (active/injured/suspended/retired) |
| `delete player <име\|id>` | Изтриване на играч |
| `seed players` | Зареждане на тестови данни |

### Валидация
- Позиция: GK, DF, MF, FW
- Номер: 1–99 (уникален в рамките на клуба)
- Дата на раждане: YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY
- Дублиран номер в същия клуб — отказва се

## Стартиране

```bash
# Създай виртуална среда
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Стартирай чатбота
python -m src.main
```

## Тестове

```bash
pip install pytest
python -m pytest tests/ -v
```
116 теста покриващи clubs_service, players_service и chatbot (parse + handle).

## Използвани технологии

1. **Python 3.x** — основен език за разработка
2. **SQLite** — релационна база данни
3. **JSON** — съхранение на intent конфигурации
4. **Regular Expressions (regex)** — обработка на естествен език
5. **Dataclasses** — структуриране на данни
6. **OS модул** — управление на пътища и файлове
7. **Datetime** — логване на командите с времеви печат
8. **Type Hints** — статична типизация
9. **Context Managers** — безопасна работа с файлове
10. **pytest** — unit тестове с изолирана DB
11. **Git** — контрол на версиите
