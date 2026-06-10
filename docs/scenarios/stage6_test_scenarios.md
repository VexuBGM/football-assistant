# Stage 6 Test Scenarios

## Chosen Stage 6 mode

The project uses the simpler accepted mode from the teacher document:

- the saved result is the main record in `matches`
- goals and cards are stored as match statistics in `goals` and `cards`
- saving a result marks the match as `played`

## Minimum scenarios

1. `Покажи кръг 1 Първа лига 2025/2026`
Expected: list of matches with `match_id`, teams, status, and result placeholder.

2. `Избери лига Първа лига 2025/2026`
Expected: league context is saved for later result entry.

3. `Избери мач 1`
Expected: current match context is saved for goals, cards, and event review.

4. `Резултат Levski-CSKA 2:1 запиши`
Expected: match result is saved, `status` becomes `played`, and the chatbot confirms the match id and round.

5. `Резултат Levski-CSKA x:y запиши`
Expected: parsing failure or clear error because the score format is invalid.

6. `Гол Ivan Petrov Levski 23 минута`
Expected: goal event is inserted for the selected match.

7. `Гол Martin Georgiev Ludogorets 23 минута`
Expected: refusal because the club/player is not part of the selected match.

8. `Гол Ivan Petrov Levski 0 минута`
Expected: refusal because minute must be between 1 and 120.

9. `Картон Petar Dimitrov CSKA Y 55`
Expected: yellow card is inserted for the selected match.

10. `Покажи събития`
Expected: chronological list of goals and cards for the selected match.
