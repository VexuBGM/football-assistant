from nicegui import ui

from ...services import matches_service
from .. import adapters
from ..layout import grid, page_shell, section
from ..notifications import notify_and_log
from ..state import state


@ui.page("/matches")
def matches_page() -> None:
    def content() -> None:
        league_select = ui.select(adapters.league_options(), label="League").props("outlined dense").classes("w-80")
        round_select = ui.number("Round", value=1, min=1, step=1, format="%.0f").props("outlined dense").classes("w-32")

        @ui.refreshable
        def matches_table() -> None:
            name, season = adapters.parse_league_option(league_select.value)
            rows = adapters.list_matches(name, season, int(round_select.value or 1))
            table = grid(
                [
                    {"field": "id", "headerName": "ID", "width": 80},
                    {"field": "round_no", "headerName": "Round", "width": 100},
                    {"field": "home", "headerName": "Home"},
                    {"field": "score", "headerName": "Score", "width": 100},
                    {"field": "away", "headerName": "Away"},
                    {"field": "status", "headerName": "Status", "width": 120},
                ],
                rows,
                small=True,
            )
            table.on("cellClicked", lambda event: select_match(event.args["data"]["id"]))

        @ui.refreshable
        def detail_panel() -> None:
            match = adapters.match_details(state.match_id)
            if match is None:
                ui.label("Select a match from the round table.").classes("fm-muted")
                return
            ui.label(f'#{match["id"]} | Round {match["round_no"]} | {match["status"]}').classes("fm-muted")
            ui.label(f'{match["home_name"]} {match["score"]} {match["away_name"]}').classes("text-2xl font-bold")
            with ui.row().classes("gap-2 items-end"):
                home_score = ui.number("Home goals", min=0, step=1, format="%.0f").props("outlined dense").classes("w-32")
                away_score = ui.number("Away goals", min=0, step=1, format="%.0f").props("outlined dense").classes("w-32")
                ui.button(
                    "Save Result",
                    icon="save",
                    on_click=lambda: save_result(match, int(home_score.value or 0), int(away_score.value or 0)),
                )
            ui.separator()
            with ui.row().classes("gap-2 items-end"):
                goal_player = ui.select(adapters.player_options(), label="Goal player").props("outlined dense").classes(
                    "w-56"
                )
                goal_club = ui.select([match["home_name"], match["away_name"]], label="Club").props("outlined dense")
                goal_minute = ui.number("Minute", value=1, min=1, max=120, step=1, format="%.0f").props("outlined dense")
                ui.button(
                    "Goal",
                    icon="sports_soccer",
                    on_click=lambda: add_goal(goal_player.value, goal_club.value, int(goal_minute.value or 1)),
                )
            with ui.row().classes("gap-2 items-end"):
                card_player = ui.select(adapters.player_options(), label="Card player").props("outlined dense").classes(
                    "w-56"
                )
                card_club = ui.select([match["home_name"], match["away_name"]], label="Club").props("outlined dense")
                card_type = ui.select(["Y", "R"], value="Y", label="Type").props("outlined dense").classes("w-24")
                card_minute = ui.number("Minute", value=1, min=1, max=120, step=1, format="%.0f").props("outlined dense")
                ui.button(
                    "Card",
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
            ui.label("Event Timeline").classes("font-bold")
            events = adapters.match_events(state.match_id)
            if not events:
                ui.label("No goals or cards recorded yet.").classes("fm-muted")
            for event in events:
                with ui.row().classes("items-center gap-2"):
                    color = "text-green-700" if event["event_type"] == "goal" else "text-amber-700"
                    ui.label(f'{event["minute"]}\'').classes("font-bold w-10")
                    ui.icon("sports_soccer" if event["event_type"] == "goal" else "style").classes(color)
                    ui.label(f'{event["label"]}: {event["player_name"]} ({event["club_name"]})')

        def refresh_workflow() -> None:
            matches_table.refresh()
            detail_panel.refresh()

        def select_league() -> None:
            name, season = adapters.parse_league_option(league_select.value)
            state.league_name = name
            state.season = season
            max_value = adapters.max_round(name, season)
            round_select.max = max_value
            round_select.update()
            result = f"Selected {name} {season}."
            notify_and_log(
                f"ui select league {name} {season}",
                "ui_select_league",
                {"league": name, "season": season},
                result,
            )
            refresh_workflow()

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
            detail_panel.refresh()

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

        league_select.on("update:model-value", lambda _: select_league())
        round_select.on("update:model-value", lambda _: matches_table.refresh())

        with ui.grid(columns="1.2fr 1fr").classes("gap-4 w-full max-lg:grid-cols-1"):
            with section("Round Fixtures", "Choose a league and click a match row"):
                with ui.row().classes("gap-2 items-end"):
                    league_select
                    round_select
                    ui.button("Use League", icon="check", on_click=select_league)
                matches_table()
            with section("Selected Match", "Save results and record goals or cards"):
                detail_panel()

    page_shell("/matches", "Match Center", "The main workspace for rounds, results, goals, cards, and event review.", content)
