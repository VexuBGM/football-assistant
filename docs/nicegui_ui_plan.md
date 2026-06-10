# NiceGUI UI Implementation Plan

## Goal

Build a polished browser-based UI for the Football Management System using NiceGUI, while preserving the existing staged project architecture:

```text
UI -> view models/adapters -> existing services -> repositories -> SQLite
```

The UI should feel closer to a modern dashboard than a basic desktop form. It should support the same workflows as the chatbot, but make common operations easier to discover and safer to use.

## Implementation Status

Implemented first version:

- `src/ui/app.py` starts the NiceGUI app at `http://127.0.0.1:8080`
- `src/ui/layout.py` provides the sidebar, top context bar, dark-mode toggle, and shared grid helpers
- `src/ui/adapters.py` provides structured read data for tables and panels
- `src/ui/pages/` contains Dashboard, Clubs, Players, Leagues, Match Center, Standings, Transfers, AI Prediction, and Chatbot pages
- Dedicated UI coverage now includes club editing, player/transfer seed helpers, player-specific and club-specific transfer history lookup, and UI action logging to `commands.log`

The current version is English-first in the browser while preserving the original chatbot command flow. Service calls are still used for mutations so existing validation and business rules remain centralized.

## Why NiceGUI

NiceGUI is a strong fit because it lets us build browser UIs in Python while still using modern web foundations. According to the official documentation, NiceGUI apps are defined in Python, rendered in the browser with Vue, styled with Quasar/Tailwind/UnoCSS/CSS, and served through FastAPI/Uvicorn with Socket.IO updates.

Useful official references:

- NiceGUI overview and documentation: <https://nicegui.io/documentation>
- NiceGUI technological foundations: <https://nicegui.io/documentation/section_foundations>
- Pages and routing: <https://nicegui.io/documentation/section_pages_routing>
- Page layout: <https://nicegui.io/documentation/section_page_layout>
- Styling and appearance: <https://nicegui.io/documentation/section_styling_appearance>
- AG Grid: <https://nicegui.io/documentation/aggrid>
- Refreshable UI: <https://nicegui.io/documentation/refreshable>
- Storage: <https://nicegui.io/documentation/storage>
- Testing: <https://nicegui.io/documentation/section_testing>
- Configuration and deployment: <https://nicegui.io/documentation/section_configuration_deployment>

## Best-Practice Direction

Use NiceGUI as a browser dashboard, not as a thin replacement for Tkinter. The app should run locally at first with `ui.run()`, then optionally support `native=True` later if we want a desktop-window feel.

Core rules:

- Keep business logic out of UI event handlers.
- Reuse existing service modules instead of duplicating SQL or rules in the UI.
- Add small adapter/view-model functions when service output is formatted as text but the UI needs structured rows.
- Prefer routed pages or a stable sidebar layout over one giant screen.
- Use AG Grid for data-heavy tables: clubs, players, matches, standings, transfers.
- Use dialogs/drawers for create/edit forms.
- Use `ui.refreshable` for sections that need reloading after mutations.
- Use `app.storage.user` or `app.storage.tab` for UI state such as selected league, selected match, filters, and theme.
- Keep the chatbot available as a first-class page so the original staged requirement is still visible.

## Proposed File Structure

```text
src/
  ui/
    __init__.py
    app.py                 # NiceGUI entry point
    layout.py              # shell, sidebar, top bar, theme
    theme.py               # colors, CSS, common classes
    adapters.py            # structured data helpers for UI tables
    notifications.py       # success/error helpers
    pages/
      __init__.py
      dashboard.py
      clubs.py
      players.py
      leagues.py
      matches.py
      standings.py
      transfers.py
      prediction.py
      chatbot.py
```

Entry command:

```powershell
python -m src.ui.app
```

Potential README addition:

```powershell
python -m pip install nicegui
python -m src.ui.app
```

If Bulgarian console output is still used during startup or testing, run with UTF-8 enabled:

```powershell
$env:PYTHONUTF8='1'
python -m src.ui.app
```

## Layout Plan

Use a calm operational dashboard style:

- Left sidebar navigation
- Top bar with app title, active league/match context, dark-mode toggle
- Main content area with dense but readable tables and forms
- Avoid a marketing/landing page; the first screen should be the usable dashboard

Pages:

1. **Dashboard**
   - Counts: clubs, players, leagues, scheduled matches, played matches
   - Current selected league and selected match
   - Short "recent activity" area from command log or recent DB rows

2. **Clubs**
   - AG Grid/table of clubs
   - Add club dialog
   - Delete club action with confirmation
   - Future: edit club if needed

3. **Players**
   - AG Grid/table with filters for club, position, status
   - Add player dialog
   - Update number, position, status
   - Delete player action with confirmation

4. **Leagues**
   - Create league form/dialog
   - Add/remove teams
   - Generate schedule button
   - Show league teams

5. **Matches**
   - Select league and round
   - Match list with status and result
   - Select match
   - Save result dialog
   - Add goal/card dialogs
   - Event timeline for the selected match

6. **Standings**
   - League/season selector
   - AG Grid standings table
   - Emphasize that standings are calculated from played matches only
   - No manual points entry

7. **Transfers**
   - Transfer player form
   - Player transfer history
   - Club transfer history
   - Validation errors surfaced as notifications and inline messages

8. **AI Prediction**
   - Home/away team selectors
   - Probability bars for home win, draw, away win
   - Small model-details section with features used
   - Show limitations when there is not enough played match data

9. **Chatbot**
   - Command input
   - Conversation history
   - Help panel with supported commands
   - This protects the original chatbot workflow and is useful for teacher demos

## Styling Plan

NiceGUI can use Quasar props and Tailwind/UnoCSS classes. The default Quasar look can feel generic, so we should customize enough to look deliberate.

Recommended visual direction:

- Light-first interface with optional dark mode
- Neutral background, white content surfaces, restrained accent color
- Football accent colors: green for success/field context, blue for selected league/match, amber/red only for warnings/cards
- 8px or smaller border radius for operational UI
- Dense tables with readable spacing
- Icons on action buttons where available
- Avoid decorative gradients, oversized hero sections, and nested cards

Suggested CSS/theme tokens:

```text
background: #f6f8fb
surface: #ffffff
surface-muted: #eef2f6
text-main: #17202a
text-muted: #64748b
accent: #2563eb
success: #15803d
warning: #b45309
danger: #b91c1c
border: #d9e2ec
```

NiceGUI tools to use:

- `ui.colors(...)` for primary/accent colors
- `ui.add_css(...)` for app-wide polish
- `.classes(...)` for Tailwind/UnoCSS utility classes
- `.props(...)` for Quasar component behavior
- `ui.dark_mode()` bound to a switch for theme control

## Data and Adapter Strategy

Many existing services return formatted strings because they were built for the chatbot. That should stay. For the UI, add adapter functions that query repositories or call service helpers and return structured lists/dicts.

Examples:

```python
def list_club_rows() -> list[dict]:
    ...

def list_player_rows(club_id: int | None = None) -> list[dict]:
    ...

def get_standings_rows(league: str, season: str) -> list[dict]:
    ...
```

Rules:

- UI adapters may read structured data.
- Mutations should still go through services, so validation and business rules stay centralized.
- If a service only returns text, classify the response with helper logic:
  - success notification for messages like `Added`, `Created`, `Saved`, `Transfer completed`
  - error notification for messages like `Error`, `Invalid`, `No ... found`, `failed`, `already`

## State Management

Use state sparingly and explicitly:

- selected league name
- selected season
- selected match ID
- table filters
- dark/light mode

Use local page state where possible. Use NiceGUI storage for state that should survive navigation:

- `app.storage.user`: user-level preferences such as dark mode
- `app.storage.tab`: selected league/match for the current browser tab
- `app.storage.client`: temporary live objects that can vanish after reload

Avoid global mutable UI state unless it is truly shared by all users.

## Refresh Pattern

Use `@ui.refreshable` or `@ui.refreshable_method` for table sections and detail panels.

Pattern:

```python
@ui.refreshable
def clubs_table():
    ui.aggrid({... rows from adapter ...})

def add_club_action():
    result = clubs_service.add_club(...)
    notify_from_service_result(result)
    clubs_table.refresh()
```

Important NiceGUI note: refreshable functions in global scope share state across clients. For independent page state, define refreshable functions inside page functions, use class methods with `@ui.refreshable_method`, or wrap global functions inside the page.

## Table Strategy

Use AG Grid for most data tables because it supports:

- column filters
- row selection
- dynamic updates
- conditional cell formatting
- better scaling than simple tables

AG Grid pages:

- clubs
- players
- matches
- standings
- transfers

Simple `ui.table` is fine for small static helper lists, but AG Grid should be the default for core datasets.

## Forms and Validation

Use dialogs for add/edit operations:

- Create club
- Add player
- Create league
- Add team to league
- Save result
- Add goal
- Add card
- Transfer player
- Prediction input can be inline because it is lightweight

Validation should happen in two layers:

1. UI-level checks for obvious empty fields, numeric ranges, and required selectors.
2. Existing service-level checks for authoritative business rules.

Never bypass service validation to make the UI feel easier.

## Error Handling

Use a small shared helper:

```python
def notify_result(result: str) -> None:
    ...
```

Surface:

- success as green notification
- validation/business error as red or amber notification
- detailed result text in a small output area when useful

For destructive actions, use confirmation dialogs:

- delete club
- delete player
- remove team from league

## Testing Plan

Keep all existing tests. Add UI-specific tests only after the first UI skeleton is in place.

Recommended test layers:

1. Existing unit/integration tests:

```powershell
python -m pytest -q
```

2. Manual all-stage verification:

```powershell
$env:PYTHONUTF8='1'
python manual_stage_verification.py
```

3. NiceGUI UI tests:

NiceGUI has a pytest plugin activated with:

```powershell
python -m pytest -p nicegui.testing.plugin
```

Start with simulated tests for:

- page loads
- navigation works
- add club through UI
- add player through UI
- generate schedule through UI
- save result and refresh standings
- prediction displays three probabilities

Later, add browser-level tests for layout and interaction if needed.

## Implementation Phases

### Phase 1: Skeleton

- Add `nicegui` dependency/instructions.
- Create `src/ui/app.py`.
- Create shared layout with sidebar and top bar.
- Add empty pages for all major workflows.
- Add a dashboard with basic counts.

### Phase 2: Read-Only Views

- Add adapters for structured data.
- Implement read-only grids for clubs, players, leagues, matches, standings, transfers.
- Add selected league/match state display.

### Phase 3: Core Mutations

- Add club and player create/delete/update flows.
- Add league creation, add teams, schedule generation.
- Add result entry, goals, cards, and event timeline.
- Add transfer form.
- Add AI prediction panel.

### Phase 4: Polish

- Add dark mode.
- Improve empty/loading/error states.
- Add consistent notifications.
- Add confirmation dialogs.
- Improve responsive layout.
- Clean Bulgarian text encoding if any mojibake remains in user-facing output.

### Phase 5: Verification

- Run existing `181` tests.
- Run manual verification script.
- Add NiceGUI UI tests for key flows.
- Manually click through each page in browser.

## Open Decisions

Decide during implementation:

- Browser-only local app vs NiceGUI native window.
- Whether the UI should be English-only, Bulgarian-only, or bilingual.
- Whether to add true edit forms for clubs, or keep only add/list/delete because that matches the chatbot surface better.
- Whether to introduce a small API layer now or call services directly from UI handlers.

Recommended defaults:

- Use browser mode first.
- Use English labels first, but preserve Bulgarian service messages where they already exist.
- Call services directly from UI handlers for mutations.
- Add adapters for reads.

## Definition of Done for the UI

The UI is ready when:

- It runs with `python -m src.ui.app`.
- It can demonstrate all completed stages without using the terminal chatbot.
- The chatbot page still works.
- All existing tests pass.
- The manual verification script passes.
- Main UI workflows are manually tested.
- README includes install/run instructions.
- User-facing Bulgarian text is readable UTF-8, not mojibake.
