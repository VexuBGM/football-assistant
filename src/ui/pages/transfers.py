from nicegui import ui

from ...services import transfers_service
from .. import adapters
from ..layout import grid, page_shell, section
from ..notifications import notify_and_log


@ui.page("/transfers")
def transfers_page() -> None:
    def content() -> None:
        @ui.refreshable
        def table() -> None:
            grid(
                [
                    {"field": "id", "headerName": "ID", "width": 80},
                    {"field": "transfer_date", "headerName": "Date", "width": 130},
                    {"field": "player", "headerName": "Player"},
                    {"field": "from_club", "headerName": "From"},
                    {"field": "to_club", "headerName": "To"},
                    {"field": "fee", "headerName": "Fee", "width": 120},
                ],
                adapters.list_transfers(),
            )

        def refresh_options() -> None:
            player_options = adapters.player_options()
            club_options = adapters.club_options()
            player.options = player_options
            from_club.options = ["free agent", *club_options]
            to_club.options = club_options
            history_player.options = player_options
            history_club.options = club_options
            player.update()
            from_club.update()
            to_club.update()
            history_player.update()
            history_club.update()

        def transfer() -> None:
            result = transfers_service.transfer_player(
                player.value or "",
                from_club.value or "",
                to_club.value or "",
                date.value or "",
                fee.value,
            )
            notify_and_log(
                f"ui transfer {player.value}",
                "ui_transfer_player",
                {
                    "player_name": player.value,
                    "from_club": from_club.value,
                    "to_club": to_club.value,
                    "date": date.value,
                    "fee": fee.value,
                },
                result,
            )
            table.refresh()
            refresh_options()

        def seed_transfers() -> None:
            result = transfers_service.seed_transfer_history()
            notify_and_log("ui seed transfers", "ui_seed_transfers", {}, result)
            table.refresh()
            refresh_options()

        def show_player_history() -> None:
            result = transfers_service.list_transfers_by_player(history_player.value or "")
            notify_and_log(
                f"ui show transfers of {history_player.value}",
                "ui_show_transfers_player",
                {"name": history_player.value},
                result,
            )
            history_output.value = result

        def show_club_history() -> None:
            result = transfers_service.list_transfers_by_club(history_club.value or "")
            notify_and_log(
                f"ui show transfers of club {history_club.value}",
                "ui_show_transfers_club",
                {"name": history_club.value},
                result,
            )
            history_output.value = result

        with ui.grid(columns="1fr 1fr").classes("gap-4 w-full max-lg:grid-cols-1"):
            with section("New Transfer", "Move a player atomically between clubs"):
                player = ui.select(adapters.player_options(), label="Player").props("outlined").classes("w-full")
                from_club = ui.select(["free agent", *adapters.club_options()], label="From club").props("outlined").classes(
                    "w-full"
                )
                to_club = ui.select(adapters.club_options(), label="To club").props("outlined").classes("w-full")
                date = ui.input("Date", value="2026-01-01").props("outlined").classes("w-full")
                fee = ui.number("Fee", min=0, step=1000, format="%.0f").props("outlined").classes("w-full")
                with ui.row().classes("fm-toolbar gap-2 flex-wrap"):
                    ui.button("Complete Transfer", icon="swap_horiz", on_click=transfer)
                    ui.button("Seed Transfers", icon="data_array", color="secondary", on_click=seed_transfers)

            with section("Targeted History", "Inspect history for one player or one club"):
                history_player = ui.select(adapters.player_options(), label="Player").props("outlined").classes("w-full")
                ui.button("Player History", icon="person_search", on_click=show_player_history)
                history_club = ui.select(adapters.club_options(), label="Club").props("outlined").classes("w-full")
                ui.button("Club History", icon="manage_search", on_click=show_club_history)
                history_output = ui.textarea("History result").props("outlined readonly autogrow").classes("w-full")

        with section("Transfer History", "All recorded player movements"):
            table()

    page_shell("/transfers", "Transfers", "Record transfer history while enforcing current-club rules.", content)
