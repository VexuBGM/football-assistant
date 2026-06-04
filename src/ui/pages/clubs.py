from nicegui import ui

from ...services import clubs_service
from .. import adapters
from ..layout import grid, page_shell, section
from ..notifications import notify_result


@ui.page("/clubs")
def clubs_page() -> None:
    def content() -> None:
        @ui.refreshable
        def table() -> None:
            rows = adapters.list_clubs()
            grid(
                [
                    {"field": "id", "headerName": "ID", "width": 80},
                    {"field": "name", "headerName": "Club"},
                    {"field": "city", "headerName": "City"},
                    {"field": "founded_year", "headerName": "Founded", "width": 120},
                ],
                rows,
            )

        def add() -> None:
            result = clubs_service.add_club(name.value, city.value, founded.value or None)
            notify_result(result)
            dialog.close()
            table.refresh()

        with section("Clubs", "Create, inspect, and delete football clubs"):
            with ui.row().classes("gap-2"):
                ui.button("Add Club", icon="add", on_click=lambda: dialog.open())
                delete_id = ui.input("Delete by name or ID").props("dense outlined").classes("w-64")
                ui.button(
                    "Delete",
                    icon="delete",
                    color="negative",
                    on_click=lambda: (notify_result(clubs_service.delete_club(delete_id.value or "")), table.refresh()),
                )
            table()

        with ui.dialog() as dialog, ui.card().classes("w-96"):
            ui.label("Add Club").classes("text-lg font-bold")
            name = ui.input("Name").props("outlined").classes("w-full")
            city = ui.input("City").props("outlined").classes("w-full")
            founded = ui.number("Founded year", min=1800, max=2100, step=1, format="%.0f").props("outlined").classes(
                "w-full"
            )
            with ui.row().classes("justify-end gap-2 w-full"):
                ui.button("Cancel", on_click=dialog.close).props("flat")
                ui.button("Save", icon="save", on_click=add)

    page_shell("/clubs", "Clubs", "The base entity for players, leagues, transfers, and matches.", content)
