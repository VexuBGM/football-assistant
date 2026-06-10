from nicegui import ui

from ...services import players_service
from .. import adapters
from ..layout import grid, page_shell, section
from ..notifications import notify_and_log


@ui.page("/players")
def players_page() -> None:
    def content() -> None:
        club_filter = ui.select(["All", *adapters.club_options()], value="All", label="Club filter").props(
            "outlined dense"
        ).classes("w-80 max-w-full")

        @ui.refreshable
        def table() -> None:
            club = None if club_filter.value == "All" else club_filter.value
            grid(
                [
                    {"field": "id", "headerName": "ID", "width": 80},
                    {"field": "number", "headerName": "#", "width": 80},
                    {"field": "full_name", "headerName": "Player"},
                    {"field": "position", "headerName": "Pos", "width": 100},
                    {"field": "club", "headerName": "Club"},
                    {"field": "status", "headerName": "Status", "width": 120},
                    {"field": "nationality", "headerName": "Nationality"},
                    {"field": "birth_date", "headerName": "Birth date", "width": 130},
                ],
                adapters.list_players(club),
            )

        club_filter.on("update:model-value", lambda _: table.refresh())

        def refresh_all() -> None:
            table.refresh()
            edit_name.options = adapters.player_options()
            edit_name.update()

        def add_player() -> None:
            result = players_service.add_player(
                player_name.value,
                player_club.value,
                player_position.value,
                int(player_number.value or 0),
                player_birth.value,
                player_nat.value,
            )
            notify_and_log(
                f"ui add player {player_name.value}",
                "ui_add_player",
                {
                    "full_name": player_name.value,
                    "club": player_club.value,
                    "position": player_position.value,
                    "number": player_number.value,
                    "birth_date": player_birth.value,
                    "nationality": player_nat.value,
                },
                result,
            )
            add_dialog.close()
            refresh_all()

        def update_player() -> None:
            result = players_service.update_player(
                edit_name.value,
                position=edit_position.value or None,
                number=int(edit_number.value) if edit_number.value is not None else None,
                status=edit_status.value or None,
            )
            notify_and_log(
                f"ui update player {edit_name.value}",
                "ui_update_player",
                {
                    "player_name": edit_name.value,
                    "position": edit_position.value,
                    "number": edit_number.value,
                    "status": edit_status.value,
                },
                result,
            )
            edit_dialog.close()
            refresh_all()

        def delete_player() -> None:
            result = players_service.delete_player(delete_id.value or "")
            notify_and_log(
                f"ui delete player {delete_id.value}",
                "ui_delete_player",
                {"identifier": delete_id.value},
                result,
            )
            refresh_all()

        def seed_players() -> None:
            result = players_service.seed_test_data()
            notify_and_log("ui seed players", "ui_seed_players", {}, result)
            refresh_all()

        with section("Players", "Filter squads, add footballers, and update their status"):
            with ui.row().classes("fm-toolbar gap-2 items-end flex-wrap"):
                ui.button("Add Player", icon="person_add", on_click=lambda: add_dialog.open())
                ui.button("Edit Player", icon="edit", on_click=lambda: edit_dialog.open())
                ui.button("Seed Players", icon="data_array", color="secondary", on_click=seed_players)
                delete_id = ui.input("Delete by name or ID").props("dense outlined").classes("w-64")
                ui.button(
                    "Delete",
                    icon="delete",
                    color="negative",
                    on_click=delete_player,
                )
            table()

        with ui.dialog() as add_dialog, ui.card().classes("w-[28rem]"):
            ui.label("Add Player").classes("text-lg font-bold")
            player_name = ui.input("Full name").props("outlined").classes("w-full")
            player_club = ui.select(adapters.club_options(), label="Club").props("outlined").classes("w-full")
            player_position = ui.select(["GK", "DF", "MF", "FW"], label="Position", value="MF").props("outlined")
            player_number = ui.number("Number", value=1, min=1, max=99, step=1, format="%.0f").props("outlined")
            player_birth = ui.input("Birth date", value="2000-01-01").props("outlined").classes("w-full")
            player_nat = ui.input("Nationality", value="Bulgarian").props("outlined").classes("w-full")
            with ui.row().classes("justify-end gap-2 w-full"):
                ui.button("Cancel", on_click=add_dialog.close).props("flat")
                ui.button("Save", icon="save", on_click=add_player)

        with ui.dialog() as edit_dialog, ui.card().classes("w-[28rem]"):
            ui.label("Edit Player").classes("text-lg font-bold")
            edit_name = ui.select(adapters.player_options(), label="Player").props("outlined").classes("w-full")
            edit_position = ui.select(["", "GK", "DF", "MF", "FW"], label="Position").props("outlined")
            edit_number = ui.number("Number", min=1, max=99, step=1, format="%.0f").props("outlined")
            edit_status = ui.select(["", "active", "injured", "suspended", "retired"], label="Status").props("outlined")
            with ui.row().classes("justify-end gap-2 w-full"):
                ui.button("Cancel", on_click=edit_dialog.close).props("flat")
                ui.button("Save", icon="save", on_click=update_player)

    page_shell("/players", "Players", "Manage squads with the existing Stage 3 validation rules.", content)
