from nicegui import ui

from ...services import matches_service, seed_service
from .. import adapters
from ..layout import page_shell, section
from ..notifications import notify_and_log
from ..state import state


@ui.page("/matches")
def matches_page() -> None:
    def content() -> None:
        league_options = adapters.league_options()
        selected_league = _initial_league(league_options)
        selected_name, selected_season = adapters.parse_league_option(selected_league)
        round_max = adapters.max_round(selected_name, selected_season)

        @ui.refreshable
        def match_picker() -> None:
            name, season = adapters.parse_league_option(league_select.value)
            round_no = int(round_select.value or 1)
            rows = adapters.list_matches(name, season, round_no)

            if not league_select.value:
                _empty_picker("No league selected", "Load demo data or create a league with scheduled matches first.")
                return
            if not rows:
                _empty_picker("No fixtures in this round", "Choose another round or generate a league schedule.")
                return

            ui.label(f"Round {round_no}: {len(rows)} fixture{'s' if len(rows) != 1 else ''}").classes(
                "text-sm fm-muted"
            )
            with ui.column().classes("gap-2 w-full"):
                for row in rows:
                    _match_row(row, select_match)

        @ui.refreshable
        def detail_panel() -> None:
            match = adapters.match_details(state.match_id)
            if match is None:
                _empty_detail()
                return

            home_players = _player_names(match["home_name"])
            away_players = _player_names(match["away_name"])
            match_players = home_players + [name for name in away_players if name not in home_players]
            home_goals = int(match["home_goals"]) if match["home_goals"] is not None else 0
            away_goals = int(match["away_goals"]) if match["away_goals"] is not None else 0
            is_played = match["status"] == "played"

            with ui.row().classes("items-start justify-between gap-3 w-full"):
                with ui.column().classes("gap-1"):
                    ui.label(f'Round {match["round_no"]} | match #{match["id"]}').classes("text-sm fm-muted")
                    ui.label(f'{match["home_name"]} {match["score"]} {match["away_name"]}').classes(
                        "text-2xl font-bold"
                    )
                _status_badge(str(match["status"]))

            ui.separator()
            ui.label("1. Save result").classes("font-bold")
            with ui.row().classes("fm-toolbar gap-2 items-end flex-wrap"):
                home_score = ui.number(
                    match["home_name"],
                    value=home_goals,
                    min=0,
                    step=1,
                    format="%.0f",
                ).props("outlined dense").classes("w-36")
                away_score = ui.number(
                    match["away_name"],
                    value=away_goals,
                    min=0,
                    step=1,
                    format="%.0f",
                ).props("outlined dense").classes("w-36")
                save_button = ui.button(
                    "Save Result",
                    icon="save",
                    on_click=lambda: save_result(match, int(home_score.value or 0), int(away_score.value or 0)),
                )
                if is_played:
                    save_button.props("disable")
            if is_played:
                ui.label("This match already has a saved result. Events can still be reviewed below.").classes(
                    "text-sm fm-muted"
                )

            ui.separator()
            ui.label("2. Record match events").classes("font-bold")
            if not match_players:
                ui.label("No players are available for these teams yet. Add players before recording events.").classes(
                    "fm-muted"
                )
            else:
                with ui.column().classes("gap-3 w-full"):
                    with ui.row().classes("fm-toolbar gap-2 items-end flex-wrap"):
                        goal_player = ui.select(
                            match_players,
                            label="Goal player",
                        ).props("outlined dense").classes("w-64 max-w-full")
                        goal_club = ui.select(
                            [match["home_name"], match["away_name"]],
                            value=match["home_name"],
                            label="Team",
                        ).props("outlined dense").classes("w-56 max-w-full")
                        goal_minute = ui.number("Minute", value=1, min=1, max=120, step=1, format="%.0f").props(
                            "outlined dense"
                        ).classes("w-32")
                        ui.button(
                            "Add Goal",
                            icon="sports_soccer",
                            on_click=lambda: add_goal(
                                goal_player.value,
                                goal_club.value,
                                int(goal_minute.value or 1),
                            ),
                        )

                    with ui.row().classes("fm-toolbar gap-2 items-end flex-wrap"):
                        card_player = ui.select(
                            match_players,
                            label="Card player",
                        ).props("outlined dense").classes("w-64 max-w-full")
                        card_club = ui.select(
                            [match["home_name"], match["away_name"]],
                            value=match["home_name"],
                            label="Team",
                        ).props("outlined dense").classes("w-56 max-w-full")
                        card_type = ui.select(["Y", "R"], value="Y", label="Card").props("outlined dense").classes(
                            "w-24"
                        )
                        card_minute = ui.number("Minute", value=1, min=1, max=120, step=1, format="%.0f").props(
                            "outlined dense"
                        ).classes("w-32")
                        ui.button(
                            "Add Card",
                            icon="style",
                            color="warning",
                            on_click=lambda: add_card(
                                card_player.value,
                                card_club.value,
                                card_type.value,
                                int(card_minute.value or 1),
                            ),
                        )

            ui.separator()
            ui.label("Event timeline").classes("font-bold")
            events = adapters.match_events(state.match_id)
            if not events:
                ui.label("No goals or cards recorded yet.").classes("fm-muted")
            for event in events:
                with ui.row().classes("items-center gap-2"):
                    color = "fm-goal" if event["event_type"] == "goal" else "fm-card-event"
                    ui.label(f'{event["minute"]}\'').classes("font-bold w-10")
                    ui.icon("sports_soccer" if event["event_type"] == "goal" else "style").classes(color)
                    ui.label(f'{event["label"]}: {event["player_name"]} ({event["club_name"]})')

        def refresh_workflow() -> None:
            match_picker.refresh()
            detail_panel.refresh()

        def select_league() -> None:
            name, season = adapters.parse_league_option(league_select.value)
            state.league_name = name
            state.season = season
            max_value = adapters.max_round(name, season)
            round_select.max = max_value
            if int(round_select.value or 1) > max_value:
                round_select.value = max_value
            round_select.update()
            result = f"Selected {name} {season}."
            notify_and_log(
                f"ui select league {name} {season}",
                "ui_select_league",
                {"league": name, "season": season},
                result,
            )
            refresh_workflow()

        def change_round(delta: int) -> None:
            max_value = int(round_select.max or 1)
            next_round = min(max(int(round_select.value or 1) + delta, 1), max_value)
            round_select.value = next_round
            round_select.update()
            match_picker.refresh()

        def select_match(match_id: int) -> None:
            result = matches_service.select_match(int(match_id))
            if not result.startswith("No match"):
                state.match_id = int(match_id)
            notify_and_log(
                f"ui select match {match_id}",
                "ui_select_match",
                {"match_id": match_id},
                result,
            )
            refresh_workflow()

        def save_result(match: dict, home_goals: int, away_goals: int) -> None:
            result = matches_service.record_result(
                match["league_name"],
                match["league_season"],
                match["home_name"],
                match["away_name"],
                home_goals,
                away_goals,
            )
            notify_and_log(
                f'ui result {match["home_name"]}-{match["away_name"]} {home_goals}:{away_goals} save',
                "ui_record_result",
                {
                    "league": match["league_name"],
                    "season": match["league_season"],
                    "home_team": match["home_name"],
                    "away_team": match["away_name"],
                    "home_goals": home_goals,
                    "away_goals": away_goals,
                },
                result,
            )
            refresh_workflow()

        def add_goal(player: str, club: str, minute: int) -> None:
            if state.match_id is None:
                notify_and_log(
                    "ui add goal without selected match",
                    "ui_add_goal",
                    {"player": player, "club": club, "minute": minute},
                    "Select a match first.",
                )
                return
            result = matches_service.add_goal(state.match_id, player or "", club or "", minute)
            notify_and_log(
                f"ui goal {player} {club} {minute}",
                "ui_add_goal",
                {"match_id": state.match_id, "player": player, "club": club, "minute": minute},
                result,
            )
            detail_panel.refresh()

        def add_card(player: str, club: str, card_type: str, minute: int) -> None:
            if state.match_id is None:
                notify_and_log(
                    "ui add card without selected match",
                    "ui_add_card",
                    {"player": player, "club": club, "card_type": card_type, "minute": minute},
                    "Select a match first.",
                )
                return
            result = matches_service.add_card(state.match_id, player or "", club or "", card_type or "Y", minute)
            notify_and_log(
                f"ui card {player} {club} {card_type} {minute}",
                "ui_add_card",
                {"match_id": state.match_id, "player": player, "club": club, "card_type": card_type, "minute": minute},
                result,
            )
            detail_panel.refresh()

        def seed_demo_data() -> None:
            result = seed_service.seed_full_demo_data()
            notify_and_log("ui seed full demo data from matches", "ui_seed_full_demo_data", {}, result)
            league_select.options = adapters.league_options()
            league_select.value = _initial_league(league_select.options)
            league_select.update()
            select_league()

        with ui.grid(columns="1.1fr 1fr").classes("gap-4 w-full max-lg:grid-cols-1"):
            with section("Round Fixtures", "Pick a league, browse rounds, then select a fixture"):
                with ui.row().classes("fm-toolbar gap-2 items-end flex-wrap"):
                    league_select = ui.select(
                        league_options,
                        value=selected_league,
                        label="League",
                    ).props("outlined dense").classes("w-96 max-w-full")
                    round_select = ui.number(
                        "Round",
                        value=1,
                        min=1,
                        max=round_max,
                        step=1,
                        format="%.0f",
                    ).props("outlined dense").classes("w-28")
                    ui.button(icon="chevron_left", on_click=lambda: change_round(-1)).props("round outline").tooltip(
                        "Previous round"
                    )
                    ui.button(icon="chevron_right", on_click=lambda: change_round(1)).props("round outline").tooltip(
                        "Next round"
                    )
                    ui.button("Load Demo Data", icon="database", on_click=seed_demo_data).props("outline")

                league_select.on("update:model-value", lambda _: select_league())
                round_select.on("update:model-value", lambda _: match_picker.refresh())
                match_picker()

            with section("Selected Match", "Save the result first, then record goals or cards"):
                detail_panel()

    page_shell("/matches", "Match Center", "The main workspace for rounds, results, goals, cards, and event review.", content)


def _initial_league(options: list[str]) -> str | None:
    context = None
    if state.league_name and state.season:
        context = f"{state.league_name} | {state.season}"
    if context in options:
        return context
    sandbox = f"{seed_service.SANDBOX_LEAGUE} | {seed_service.SANDBOX_SEASON}"
    if sandbox in options:
        return sandbox
    return options[0] if options else None


def _player_names(club_name: str) -> list[str]:
    return [row["full_name"] for row in adapters.list_players(club_name)]


def _empty_picker(title: str, detail: str) -> None:
    with ui.column().classes("gap-2 py-6 items-start"):
        ui.icon("sports_soccer").classes("text-4xl text-primary")
        ui.label(title).classes("text-lg font-bold")
        ui.label(detail).classes("fm-muted")


def _empty_detail() -> None:
    with ui.column().classes("gap-2 py-6 items-start"):
        ui.icon("touch_app").classes("text-4xl text-primary")
        ui.label("Select a fixture").classes("text-lg font-bold")
        ui.label("Use the match list on the left. The selected match opens here for result and event entry.").classes(
            "fm-muted"
        )


def _match_row(row: dict, select_match) -> None:
    selected = state.match_id == int(row["id"])
    status_icon = "check_circle" if row["status"] == "played" else "event"
    row_classes = "items-center justify-between gap-3 w-full p-3 rounded-md border cursor-pointer"
    row_style = "border-color: var(--fm-border); background: var(--fm-surface-raised);"
    if selected:
        row_style = "border-color: #2563eb; background: rgba(37, 99, 235, 0.14);"

    with ui.row().classes(row_classes).style(row_style).on("click", lambda: select_match(int(row["id"]))):
        with ui.row().classes("items-center gap-3 min-w-0"):
            ui.icon(status_icon).classes("text-primary text-xl")
            with ui.column().classes("gap-0 min-w-0"):
                ui.label(f'{row["home"]} vs {row["away"]}').classes("font-bold")
                ui.label(f'Match #{row["id"]}').classes("text-xs fm-muted")
        with ui.row().classes("items-center gap-3"):
            score = row["score"] if row["score"] != "-" else "not played"
            ui.label(score).classes("font-bold")
            _status_badge(str(row["status"]))
            ui.button("Select", icon="touch_app", on_click=lambda: select_match(int(row["id"]))).props("dense")


def _status_badge(status: str) -> None:
    color = "positive" if status == "played" else "primary"
    text = "Played" if status == "played" else "Scheduled"
    ui.badge(text, color=color).classes("px-2 py-1")
