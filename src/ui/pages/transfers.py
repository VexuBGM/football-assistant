from nicegui import ui

from ...services import transfers_service
from .. import adapters
from ..layout import grid, page_shell, section
from ..notifications import notify_result


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

        def transfer() -> None:
            result = transfers_service.transfer_player(
                player.value or "",
                from_club.value or "",
                to_club.value or "",
                date.value or "",
                fee.value,
            )
            notify_result(result)
            table.refresh()

        with ui.grid(columns="1fr 1.8fr").classes("gap-4 w-full max-lg:grid-cols-1"):
            with section("New Transfer", "Move a player atomically between clubs"):
                player = ui.select(adapters.player_options(), label="Player").props("outlined").classes("w-full")
                from_club = ui.select(["free agent", *adapters.club_options()], label="From club").props("outlined").classes(
                    "w-full"
                )
                to_club = ui.select(adapters.club_options(), label="To club").props("outlined").classes("w-full")
                date = ui.input("Date", value="2026-01-01").props("outlined").classes("w-full")
                fee = ui.number("Fee", min=0, step=1000, format="%.0f").props("outlined").classes("w-full")
                ui.button("Complete Transfer", icon="swap_horiz", on_click=transfer)

            with section("Transfer History", "All recorded player movements"):
                table()

    page_shell("/transfers", "Transfers", "Record transfer history while enforcing current-club rules.", content)
