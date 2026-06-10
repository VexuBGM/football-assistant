from nicegui import ui

from ...services import clubs_service
from .. import adapters
from ..layout import grid, page_shell, section
from ..notifications import notify_and_log


@ui.page("/clubs")
def clubs_page() -> None:
    def content() -> None:
        def club_options() -> list[str]:
            return [f'{row["id"]} | {row["name"]}' for row in adapters.list_clubs()]

        def selected_club_id(value: str | None) -> int | None:
            if not value or " | " not in value:
                return None
            return int(value.split(" | ", 1)[0])

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

        def refresh_all() -> None:
            table.refresh()
            edit_club.options = club_options()
            edit_club.update()

        def add() -> None:
            result = clubs_service.add_club(name.value, city.value, founded.value or None)
            notify_and_log(
                f"ui add club {name.value}",
                "ui_add_club",
                {"name": name.value, "city": city.value, "founded_year": founded.value},
                result,
            )
            dialog.close()
            refresh_all()

        def load_selected_club() -> None:
            club_id = selected_club_id(edit_club.value)
            row = next((club for club in adapters.list_clubs() if club["id"] == club_id), None)
            if row is None:
                return
            edit_name.value = row["name"]
            edit_city.value = row["city"]
            edit_founded.value = row["founded_year"]

        def update() -> None:
            club_id = selected_club_id(edit_club.value)
            if club_id is None:
                result = "Error: choose a club to edit."
            else:
                result = clubs_service.update_club(
                    club_id,
                    edit_name.value,
                    edit_city.value,
                    int(edit_founded.value) if edit_founded.value is not None else None,
                )
            notify_and_log(
                f"ui update club {club_id}",
                "ui_update_club",
                {
                    "club_id": club_id,
                    "name": edit_name.value,
                    "city": edit_city.value,
                    "founded_year": edit_founded.value,
                },
                result,
            )
            edit_dialog.close()
            refresh_all()

        def delete() -> None:
            result = clubs_service.delete_club(delete_id.value or "")
            notify_and_log(
                f"ui delete club {delete_id.value}",
                "ui_delete_club",
                {"identifier": delete_id.value},
                result,
            )
            refresh_all()

        with section("Clubs", "Create, inspect, and delete football clubs"):
            with ui.row().classes("gap-2"):
                ui.button("Add Club", icon="add", on_click=lambda: dialog.open())
                ui.button("Edit Club", icon="edit", on_click=lambda: edit_dialog.open())
                delete_id = ui.input("Delete by name or ID").props("dense outlined").classes("w-64")
                ui.button(
                    "Delete",
                    icon="delete",
                    color="negative",
                    on_click=delete,
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

        with ui.dialog() as edit_dialog, ui.card().classes("w-96"):
            ui.label("Edit Club").classes("text-lg font-bold")
            edit_club = ui.select(club_options(), label="Club").props("outlined").classes("w-full")
            edit_club.on("update:model-value", lambda _: load_selected_club())
            edit_name = ui.input("Name").props("outlined").classes("w-full")
            edit_city = ui.input("City").props("outlined").classes("w-full")
            edit_founded = ui.number("Founded year", min=1800, max=2100, step=1, format="%.0f").props("outlined").classes(
                "w-full"
            )
            with ui.row().classes("justify-end gap-2 w-full"):
                ui.button("Cancel", on_click=edit_dialog.close).props("flat")
                ui.button("Save", icon="save", on_click=update)

    page_shell("/clubs", "Clubs", "The base entity for players, leagues, transfers, and matches.", content)
