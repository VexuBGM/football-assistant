from nicegui import ui

from .. import adapters
from ..layout import grid, page_shell, section
from ..notifications import notify_and_log
from ..state import state


@ui.page("/standings")
def standings_page() -> None:
    def content() -> None:
        selected_value = None
        if state.league_name and state.season:
            selected_value = f"{state.league_name} | {state.season}"
        league_select = ui.select(
            adapters.league_options(),
            value=selected_value,
            label="League",
        ).props("outlined dense").classes("w-96 max-w-full")

        @ui.refreshable
        def standings_table() -> None:
            name, season = adapters.parse_league_option(league_select.value)
            rows, error = adapters.standings_rows(name, season)
            if error:
                ui.label(error).classes("fm-muted")
                return
            grid(
                [
                    {"field": "pos", "headerName": "#", "width": 80},
                    {"field": "team", "headerName": "Team"},
                    {"field": "mp", "headerName": "MP", "width": 80},
                    {"field": "w", "headerName": "W", "width": 80},
                    {"field": "d", "headerName": "D", "width": 80},
                    {"field": "l", "headerName": "L", "width": 80},
                    {"field": "gf_ga", "headerName": "GF:GA", "width": 100},
                    {"field": "gd", "headerName": "GD", "width": 90},
                    {"field": "pts", "headerName": "PTS", "width": 90},
                ],
                rows,
            )

        def use_context() -> None:
            name, season = adapters.parse_league_option(league_select.value)
            state.league_name = name
            state.season = season
            result = f"Selected {name} {season} as working context."
            notify_and_log(
                f"ui select standings context {name} {season}",
                "ui_select_standings_context",
                {"league": name, "season": season},
                result,
            )

        league_select.on("update:model-value", lambda _: standings_table.refresh())

        with section("Calculated Standings", "Only played matches with saved scores are counted"):
            with ui.row().classes("fm-toolbar gap-2 items-end flex-wrap"):
                league_select
                ui.button("Use As Context", icon="check", on_click=use_context)
                ui.button("Refresh", icon="refresh", on_click=lambda: standings_table.refresh())
            standings_table()

    page_shell("/standings", "Standings", "Points are calculated from match results, never entered manually.", content)
