from nicegui import ui

from ..database.db import init_db

# Import page modules so their @ui.page decorators register routes.
from .pages import chatbot, clubs, dashboard, leagues, matches, players, prediction, standings, transfers  # noqa: F401,E402


def main() -> None:
    init_db()
    ui.run(
        title="Football Manager",
        host="127.0.0.1",
        port=8080,
        reload=False,
        show=False,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
