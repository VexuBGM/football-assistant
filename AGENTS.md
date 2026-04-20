# AGENTS.md

## Purpose

This repository is a staged school project for a Football Management System. When the user asks for a specific stage, you must implement that stage according to the teacher's materials in `docs/stages/`, update the required documentation, and verify the result thoroughly before stopping.

The user may ask for stages one at a time, for example: "do Stage 6", then later "do Stage 7". Do not automatically jump ahead to later stages unless the user explicitly asks for them.

## Source Of Truth

Always treat the teacher's stage documents as the primary specification.

Read the relevant files before making changes:

- `docs/stages/ЕТАП 1 — Седмици 1–2.md`
- `docs/stages/Емил Спасов - ЕТАП 1 — Седмици 1–2 Анализ, проектиране и база данни (опростени изисквания)_.md`
- `docs/stages/ЕТАП 2 _ Python + SQL връзка + CRUD „Клубове“.md`
- `docs/stages/ЕТАП 3 — CRUD „Футболисти“ + филтри.md`
- `docs/stages/Етап 4 — Трансфери  изисквания.md`
- `docs/stages/Етап 5_ Лиги (Leagues) — Изисквания.md`
- `docs/stages/Етап 6_ Мачове — Изисквания.md`
- `docs/stages/Етап 7_ Класиране — Изисквания.md`
- `docs/stages/Етап 8_ AI Модул (Прогноза на мач).md`

Use supporting example files when they exist:

- `docs/example_dialog_stage3.md`
- `docs/example_dialog_stage4.md`
- `docs/example_dialog_stage5.md`
- `docs/stage4_test_scenarios.md`
- `docs/stage5_test_scenarios.md`

If the stage document and the current codebase disagree, the requested stage document wins unless following it would break a previously completed stage in an unnecessary way. In that case, refactor carefully so the project still satisfies both the previous completed work and the newly requested stage.

## Project Intent

This is not a generic prototype. It is a class assignment. Optimize for:

- following the teacher's requirements exactly
- producing the artifacts the teacher expects
- preserving a clean, understandable student project structure
- making the feature demonstrably work, not just "probably work"

## Stage-By-Stage Rule

When the user requests a stage:

1. Read the corresponding stage file and any related example dialog or scenario files.
2. Extract the acceptance criteria, mandatory commands, data rules, and required artifacts.
3. Inspect the current repository to see what already exists.
4. Implement only what is needed for that stage, plus any small refactors required to keep the code coherent.
5. Update or create the documentation artifacts for that stage automatically.
6. Run strong verification: unit tests, integration tests, chatbot-level tests, and manual command walkthroughs when possible.
7. Do not declare success until the stage is implemented and verified.

Do not make the user manually test your work if you can test it yourself.

## Documentation Requirements

Whenever a stage requires docs, create or update them yourself. Do not wait for the user to ask.

Expected documentation may include:

- project description or analysis markdown
- ER diagram notes or references
- `sql/schema.sql`
- seed or test data
- example dialog files under `docs/`
- stage test scenario files under `docs/`
- `README.md` updates when commands or setup change

If a stage doc asks for a "short description", "example dialog", "test scenarios", or similar deliverables, produce them in the repo.

## Implementation Expectations

Preserve or improve the existing modular architecture where possible. The current codebase already uses patterns like:

- `chatbot -> router -> services -> repositories/database`
- explicit service modules
- test files under `tests/`

Prefer extending the current structure over creating duplicate parallel implementations.

You may refactor existing code if that is needed to satisfy the requested stage or to keep later stage work maintainable. Keep refactors purposeful and scoped.

## Stage Notes

### Stage 1

Deliverables matter as much as code:

- project analysis/description
- minimum 5 core functions
- main entities/tables
- ER diagram support
- database choice and short justification
- `schema.sql`
- test inserts

The file `docs/stages/Емил Спасов - ЕТАП 1 — Седмици 1–2 Анализ, проектиране и база данни (опростени изисквания)_.md` is an example answer and should be used as a style and completeness reference.

### Stage 2

Must cover:

- Python to SQL connection
- clubs CRUD
- basic chatbot loop
- regex-based parsing
- logging to `commands.log`
- README instructions and command examples

### Stage 3

Must cover:

- `players` module linked to clubs
- CRUD for players
- validation for position, squad number, and birth date
- filtering by club
- example dialog with clubs and players

### Stage 4

Must cover:

- `transfers` table and transfer history
- strict transfer business rules
- atomic transfer operation
- chatbot commands for transfer and transfer history
- documented test scenarios

### Stage 5

Must cover:

- leagues
- league teams
- schedule generation with round-robin
- validation against duplicate schedules and invalid team counts
- documented test scenarios and example dialog

### Stage 6

Must cover:

- match selection or context
- result entry
- goals and cards
- validation of player/team/minute logic
- event review

### Stage 7

Must cover:

- standings calculated from played matches only
- no manual points entry
- sorting and tiebreak logic required by the stage
- proper output format and validation for edge cases

### Stage 8

Must cover:

- match prediction command
- probabilities for home win, draw, away win
- real data from the database
- documented model logic and limitations

Prefer the rule-based minimum unless the user explicitly wants the more advanced ML version.

## Testing And Verification

Verification is mandatory. The user has said they may not test the result themselves, so you must be highly confident before finishing.

For every requested stage, do as many of the following as apply:

- run the relevant automated test suite with `pytest`
- add missing unit tests for new services, validators, helpers, and repositories
- add integration-style tests that exercise database interactions
- add chatbot or end-to-end style tests for the required commands
- manually exercise the feature through the CLI when practical
- verify logs and generated docs if the stage requires them
- check edge cases named in the teacher's stage file

Do not stop at "tests pass" if important flows are still unproven.

If manual verification is possible in the terminal, do it.

If something cannot be fully verified, say exactly what was verified, what could not be verified, and why. This should be rare.

## Definition Of Done

A stage is done only if all of the following are true:

- the requested stage requirements from the relevant `docs/stages/` file are implemented
- the required commands or user flows work
- the required docs/artifacts for that stage are present or updated
- automated tests covering the stage pass
- any practical manual verification has been performed
- the final summary clearly states assumptions, coverage, and any remaining limitations

## Communication Expectations

When working on a stage:

- state which stage you are implementing
- mention which teacher doc(s) you are using
- summarize the acceptance criteria you are targeting
- keep the user updated as you inspect, implement, test, and verify

In the final response:

- summarize what was implemented
- list what was tested
- mention which docs were created or updated
- call out any unavoidable limitation or ambiguity

## Avoid

Do not:

- skip reading the stage file
- stop after only editing code without tests
- leave required docs unfinished
- ask the user to perform testing you can perform yourself
- implement speculative future-stage features unless needed for the requested stage
- bypass business logic by placing SQL directly in chatbot handlers

## Practical Checklist

Before finishing any stage, verify this checklist:

- Relevant stage file read
- Related example/scenario docs read
- Required schema/data/code changes implemented
- Required docs created or updated
- Automated tests added or updated
- Automated tests run successfully
- Manual command walkthrough attempted
- Final response includes verification details
