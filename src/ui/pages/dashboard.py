from nicegui import ui

from .. import adapters
from ..layout import grid, page_shell, section
from ..state import state


@ui.page("/")
def dashboard_page() -> None:
    def content() -> None:
        counts = adapters.dashboard_counts()
        with ui.grid(columns="repeat(auto-fit, minmax(160px, 1fr))").classes("gap-3 w-full"):
            for label, value, icon in [
                ("Clubs", counts["clubs"], "shield"),
                ("Players", counts["players"], "groups"),
                ("Leagues", counts["leagues"], "emoji_events"),
                ("Scheduled", counts["scheduled_matches"], "event"),
                ("Played", counts["played_matches"], "check_circle"),
                ("Transfers", counts["transfers"], "swap_horiz"),
            ]:
                with ui.column().classes("fm-panel fm-stat p-4 gap-1"):
                    with ui.row().classes("items-center justify-between w-full"):
                        ui.label(label).classes("fm-muted text-sm")
                        ui.icon(icon).classes("text-primary")
                    ui.label(str(value)).classes("text-3xl font-bold")

        with ui.grid(columns="2fr 1fr").classes("gap-4 w-full max-lg:grid-cols-1"):
            with section("Recent Results", "Latest played matches saved in the database"):
                rows = adapters.recent_results()
                if not rows:
                    ui.label("No results yet. Use Match Center to save one.").classes("fm-muted")
                else:
                    grid(
                        [
                            {"field": "id", "headerName": "ID", "width": 80},
                            {"field": "league", "headerName": "League"},
                            {"field": "season", "headerName": "Season", "width": 120},
                            {"field": "round_no", "headerName": "Round", "width": 100},
                            {"field": "home", "headerName": "Home"},
                            {"field": "home_goals", "headerName": "HG", "width": 80},
                            {"field": "away_goals", "headerName": "AG", "width": 80},
                            {"field": "away", "headerName": "Away"},
                        ],
                        rows,
                        small=True,
                    )

            with section("Working Context", "The selected league and match drive Match Center actions"):
                ui.label(state.league_name or "No league selected").classes("text-xl font-bold")
                ui.label(state.season or "Choose a league from Match Center or Standings").classes("fm-muted")
                ui.separator()
                ui.label(f"Selected match: #{state.match_id}" if state.match_id else "No match selected").classes(
                    "font-medium"
                )
                with ui.row().classes("gap-2"):
                    ui.button("Open Match Center", icon="sports_soccer", on_click=lambda: ui.navigate.to("/matches"))
                    ui.button("View Standings", icon="format_list_numbered", on_click=lambda: ui.navigate.to("/standings"))

    page_shell("/", "Dashboard", "A fast overview of the football management database.", content)
