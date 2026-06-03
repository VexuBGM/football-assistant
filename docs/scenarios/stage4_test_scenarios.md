# Stage 4 Test Scenarios

## Minimum demo data

- Clubs: `Levski Sofia`, `CSKA Sofia`, `Ludogorets`, `Botev Plovdiv`
- Players: at least 6 players distributed across those clubs
- Transfers: at least 5 entries via `seed_transfer_history()`

## Required scenarios

1. Valid transfer
Command: `Трансфер Иван Петров от Левски в Лудогорец 2026-03-10`
Expected: transfer is saved, `players.club_id` changes to `Лудогорец`, and history contains the new row.

2. Wrong source club
Command: `Трансфер Иван Петров от ЦСКА в Лудогорец 2026-03-10`
Expected: refusal with clear message that the current club does not match the provided `from` club.

3. Missing destination club
Command: `Трансфер Иван Петров от Левски в Несъществуващ 2026-03-10`
Expected: refusal with `No club found`.

4. Same source and destination
Command: `Трансфер Иван Петров от Левски в Левски 2026-03-10`
Expected: refusal because source and destination must be different.

5. Player transfer history
Command: `Покажи трансфери на Иван Петров`
Expected: chronological list with date, source club, destination club, and optional fee.
