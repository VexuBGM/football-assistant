from collections.abc import Callable

from nicegui import ui

from .state import state
from .theme import apply_theme


NAV_ITEMS = [
    ("/", "Dashboard", "dashboard"),
    ("/clubs", "Clubs", "shield"),
    ("/players", "Players", "groups"),
    ("/leagues", "Leagues", "emoji_events"),
    ("/matches", "Match Center", "sports_soccer"),
    ("/standings", "Standings", "format_list_numbered"),
    ("/transfers", "Transfers", "swap_horiz"),
    ("/prediction", "AI Prediction", "insights"),
    ("/chatbot", "Chatbot", "terminal"),
]


def nav_link(path: str, label: str, icon: str, active_path: str) -> None:
    active = "fm-link-active" if active_path == path else ""
    with ui.link(target=path).classes(f"w-full no-underline text-slate-700 {active}"):
        with ui.row().classes("items-center gap-3 px-3 py-2 rounded-md w-full"):
            ui.icon(icon).classes("text-lg")
            ui.label(label).classes("text-sm")


def page_shell(active_path: str, title: str, subtitle: str | None, content: Callable[[], None]) -> None:
    apply_theme()

    with ui.header().classes("bg-white text-slate-900 border-b border-slate-200 px-4"):
        with ui.row().classes("items-center justify-between w-full"):
            with ui.row().classes("items-center gap-3"):
                ui.icon("sports_soccer").classes("text-primary text-2xl")
                with ui.column().classes("gap-0"):
                    ui.label("Football Manager").classes("font-bold text-base")
                    context = "No league selected"
                    if state.league_name and state.season:
                        context = f"{state.league_name} {state.season}"
                    if state.match_id:
                        context += f" | match #{state.match_id}"
                    ui.label(context).classes("text-xs fm-muted")
            dark = ui.dark_mode()
            ui.switch("Dark", value=False, on_change=lambda event: dark.set_value(event.value)).props("dense")

    with ui.left_drawer().classes("bg-white border-r border-slate-200 px-3 py-4"):
        ui.label("Navigation").classes("uppercase text-xs tracking-wide fm-muted px-3 mb-2")
        for path, label, icon in NAV_ITEMS:
            nav_link(path, label, icon, active_path)

    with ui.page_sticky(position="bottom-right", x_offset=18, y_offset=18):
        ui.button(icon="terminal", on_click=lambda: ui.navigate.to("/chatbot")).props("round color=primary").tooltip(
            "Open chatbot"
        )

    with ui.column().classes("fm-page gap-4"):
        with ui.column().classes("gap-1"):
            ui.label(title).classes("text-2xl font-bold")
            if subtitle:
                ui.label(subtitle).classes("fm-muted")
        content()


def section(title: str, subtitle: str | None = None):
    panel = ui.column().classes("fm-panel p-4 gap-3")
    with panel:
        with ui.row().classes("items-start justify-between w-full"):
            with ui.column().classes("gap-0"):
                ui.label(title).classes("font-bold text-base")
                if subtitle:
                    ui.label(subtitle).classes("text-sm fm-muted")
    return panel


def grid(column_defs: list[dict], row_data: list[dict], small: bool = False):
    return ui.aggrid(
        {
            "defaultColDef": {
                "sortable": True,
                "filter": True,
                "resizable": True,
            },
            "columnDefs": column_defs,
            "rowData": row_data,
            "rowSelection": "single",
            "animateRows": True,
        }
    ).classes("fm-small-grid" if small else "fm-grid")
