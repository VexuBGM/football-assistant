# Football Clubs Management (ЕТАП 2)

## Описание на проекта
Проект: информационна система (чатбот) за управление на футболни клубове. Реализира Python  SQLite връзка и CRUD операции за клубове. Системата е изградена със съвременни инструменти за обработка на естествен език и управление на база данни.

## Структура
- `sql/schema.sql`  таблици Clubs/Players/Matches
- `src/db.py`  централизирана DB връзка + заявки
- `src/clubs_service.py`  CRUD за Clubs (валидация + без дубликати)
- `src/chatbot.py`  intent parser (regex) + handler
- `src/main.py`  chat loop + logging към `commands.log`

## Стартиране

### Стъпка 1: Подготовка на средата
```bash
# Създай виртуална среда
python -m venv venv
# Активирай я
venv\Scripts\activate
```

### Стъпка 2: Инициализация на базата данни
```bash
# Импортирай схемата от sql/schema.sql
sqlite3 football.db < sql/schema.sql
```
Или от PowerShell:
```powershell
Get-Content sql/schema.sql | sqlite3 football.db
```

### Стъпка 3: Стартиране на чатбота
```bash
python -m src.main
```

## Използвани технологии

1. **Python 3.x**  основен език за разработка
2. **SQLite**  релационна база данни
3. **JSON**  съхранение на intent конфигурации
4. **Regular Expressions (regex)**  обработка на естествен език
5. **Dataclasses**  структуриране на данни
6. **OS модул**  управление на пътища и файлове
7. **Datetime**  логване на командите с времеви печат
8. **Type Hints**  статична типизация
9. **Context Managers**  безопасна работа с файлове
10. **Git**  контрол на версиите
