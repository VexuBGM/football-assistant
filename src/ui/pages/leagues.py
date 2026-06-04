from nicegui import ui

from ...services import leagues_service
from .. import adapters
from ..layout import grid, page_shell, section
from ..notifications import notify_result
from ..state import state


@ui.page("/leagues")
def leagues_page() -> None:
    def content() -> None:
        selected = ui.select(adapters.league_options(), label="League").props("outlined dense").classes("w-80")

        @ui.refreshable
        def leagues_table() -> None:
            grid(
                [
                    {"field": "id", "headerName": "ID", "width": 80},
                    {"field": "name", "headerName": "League"},
                    {"field": "season", "headerName": "Season", "width": 130},
                    {"field": "teams", "headerName": "Teams", "width": 100},
                    {"field": "matches", "headerName": "Matches", "width": 110},
                ],
                adapters.list_leagues(),
                small=True,
            )

        @ui.refreshable
        def teams_table() -> None:
            name, season = adapters.parse_league_option(selected.value)
            grid(
                [
                    {"field": "id", "headerName": "ID", "width": 80},
                    {"field": "name", "headerName": "Club"},
                    {"field": "city", "headerName": "City"},
                    {"field": "founded_year", "headerName": "Founded", "width": 120},
                ],
                adapters.list_league_teams(name, season),
                small=True,
            )

        def refresh_all() -> None:
            selected.options = adapters.league_options()
            selected.update()
            leagues_table.refresh()
            teams_table.refresh()

        selected.on("update:model-value", lambda _: teams_table.refresh())

        def create() -> None:
            result = leagues_service.create_league(league_name.value, league_season.value)
            notify_result(result)
            create_dialog.close()
            refresh_all()

        def add_team() -> None:
            name, season = adapters.parse_league_option(selected.value)
            result = leagues_service.add_team_to_league(team_add.value or "", name or "", season or "")
            notify_result(result)
            refresh_all()

        def remove_team() -> None:
            name, season = adapters.parse_league_option(selected.value)
            result = leagues_service.remove_team_from_league(team_remove.value or "", name or "", season or "")
            notify_result(result)
            refresh_all()

        def generate() -> None:
            name, season = adapters.parse_league_option(selected.value)
            result = leagues_service.generate_schedule(name or "", season or "")
            notify_result(result)
            refresh_all()

        def use_context() -> None:
            name, season = adapters.parse_league_option(selected.value)
            state.league_name = name
            state.season = season
            notify_result(f"Selected {name} {season} as working context.")

        with ui.grid(columns="1fr 1fr").classes("gap-4 w-full max-lg:grid-cols-1"):
            with section("Leagues", "Create competitions and inspect their schedule readiness"):
                with ui.row().classes("gap-2"):
                    ui.button("Create League", icon="add", on_click=lambda: create_dialog.open())
                    ui.button("Use As Context", icon="check", on_click=use_context)
                leagues_table()

            with section("League Teams", "Add or remove clubs before generating a schedule"):
                selected
                with ui.row().classes("gap-2 items-end"):
                    team_add = ui.select(adapters.club_options(), label="Add team").props("outlined dense").classes("w-56")
                    ui.button("Add", icon="add", on_click=add_team)
                with ui.row().classes("gap-2 items-end"):
                    team_remove = ui.select(adapters.club_options(), label="Remove team").props("outlined dense").classes(
                        "w-56"
                    )
                    ui.button("Remove", icon="remove", color="warning", on_click=remove_team)
                ui.button("Generate Schedule", icon="event", on_click=generate)
                teams_table()

        with ui.dialog() as create_dialog, ui.card().classes("w-96"):
            ui.label("Create League").classes("text-lg font-bold")
            league_name = ui.input("Name").props("outlined").classes("w-full")
            league_season = ui.input("Season", value="2025/2026").props("outlined").classes("w-full")
            with ui.row().classes("justify-end gap-2 w-full"):
                ui.button("Cancel", on_click=create_dialog.close).props("flat")
                ui.button("Save", icon="save", on_click=create)

    page_shell("/leagues", "Leagues", "Build competitions, add teams, and generate round-robin fixtures.", content)
