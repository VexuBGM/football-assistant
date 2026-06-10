from nicegui import ui

from .. import adapters
from ..layout import page_shell, section
from ..notifications import notify_and_log
from ..state import state
from ...services import seed_service


@ui.page("/prediction")
def prediction_page() -> None:
    def content() -> None:
        league_options = adapters.prediction_league_options() or adapters.league_options()
        selected_league = _initial_league(league_options)
        selected_name, selected_season = adapters.parse_league_option(selected_league)
        team_options = adapters.club_options_for_league(selected_name, selected_season) or adapters.club_options()
        suggested_home, suggested_away = adapters.suggested_prediction_pair(selected_name, selected_season)

        @ui.refreshable
        def result_panel() -> None:
            if not home.value or not away.value:
                _empty_state(
                    "Choose two teams",
                    "Pick a league, then choose a home and away team. The prediction uses only real played matches.",
                )
                return

            prediction, error = adapters.prediction_view(str(home.value), str(away.value))
            if error or prediction is None:
                _error_state(error or "Prediction failed.")
                return

            _prediction_result(prediction)

        def refresh_teams() -> None:
            name, season = adapters.parse_league_option(league.value)
            options = adapters.club_options_for_league(name, season) or adapters.club_options()
            suggested = adapters.suggested_prediction_pair(name, season)
            home.options = options
            away.options = options
            home.value = suggested[0] or _first_option(options)
            away.value = suggested[1] or _second_option(options)
            home.update()
            away.update()
            result_panel.refresh()

        def swap_teams() -> None:
            home.value, away.value = away.value, home.value
            home.update()
            away.update()
            result_panel.refresh()

        def load_demo_data() -> None:
            result = seed_service.seed_full_demo_data()
            notify_and_log(
                "ui seed demo data from prediction",
                "ui_seed_demo_prediction",
                {},
                result,
            )
            league.options = adapters.prediction_league_options() or adapters.league_options()
            league.value = _initial_league(league.options)
            league.update()
            refresh_teams()

        def predict() -> None:
            prediction, error = adapters.prediction_view(str(home.value or ""), str(away.value or ""))
            result = error or (
                f'Prediction calculated: {prediction["home_win"]}% home, '
                f'{prediction["draw"]}% draw, {prediction["away_win"]}% away.'
                if prediction is not None
                else "Prediction failed."
            )
            notify_and_log(
                f"ui prediction {home.value} vs {away.value}",
                "ui_predict_match",
                {"home_team": home.value, "away_team": away.value},
                result,
            )
            result_panel.refresh()

        with ui.grid(columns="minmax(280px, 0.9fr) minmax(320px, 1.4fr)").classes("gap-4 w-full max-lg:grid-cols-1"):
            with section("Prediction Setup", "Choose a league first so both team menus stay valid"):
                league = ui.select(
                    league_options,
                    value=selected_league,
                    label="League with played matches",
                ).props("outlined dense").classes("w-full")
                with ui.row().classes("gap-2 w-full items-end max-md:flex-col max-md:items-stretch"):
                    home = ui.select(
                        team_options,
                        value=suggested_home or _first_option(team_options),
                        label="Home team",
                    ).props("outlined dense").classes("flex-1 min-w-0")
                    ui.button(icon="swap_horiz", on_click=swap_teams).props("round outline").tooltip(
                        "Swap home and away teams"
                    )
                    away = ui.select(
                        team_options,
                        value=suggested_away or _second_option(team_options),
                        label="Away team",
                    ).props("outlined dense").classes("flex-1 min-w-0")
                with ui.row().classes("gap-2 flex-wrap"):
                    ui.button("Predict", icon="insights", on_click=predict)
                    ui.button("Load Demo Data", icon="database", on_click=load_demo_data).props("outline").tooltip(
                        "Create the seeded league, teams, played matches, transfers, goals, and cards"
                    )
                ui.label(
                    "Prediction needs two different teams from the same league with at least five played matches each."
                ).classes("text-sm fm-muted")

            with section("Probabilities", "Rule-based prediction from real match data"):
                result_panel()

        league.on("update:model-value", lambda _: refresh_teams())
        home.on("update:model-value", lambda _: result_panel.refresh())
        away.on("update:model-value", lambda _: result_panel.refresh())

    page_shell("/prediction", "AI Prediction", "Estimate home win, draw, and away win probabilities.", content)


def _initial_league(options: list[str]) -> str | None:
    context = None
    if state.league_name and state.season:
        context = f"{state.league_name} | {state.season}"
    if context in options:
        return context
    demo = f"{seed_service.DEMO_LEAGUE} | {seed_service.DEMO_SEASON}"
    if demo in options:
        return demo
    return _first_option(options)


def _first_option(options: list[str]) -> str | None:
    return options[0] if options else None


def _second_option(options: list[str]) -> str | None:
    return options[1] if len(options) > 1 else None


def _empty_state(title: str, detail: str) -> None:
    with ui.column().classes("gap-2 py-6 items-start"):
        ui.icon("insights").classes("text-4xl text-primary")
        ui.label(title).classes("text-lg font-bold")
        ui.label(detail).classes("fm-muted")


def _error_state(message: str) -> None:
    with ui.column().classes("gap-3"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("error_outline").classes("text-negative text-2xl")
            ui.label("Prediction cannot be calculated yet").classes("font-bold")
        ui.label(message).classes("text-negative")
        ui.label(
            "Use a league with played results, or click Load Demo Data for a ready-made example."
        ).classes("text-sm fm-muted")


def _prediction_result(prediction: dict) -> None:
    ui.label(f'{prediction["home"]} vs {prediction["away"]}').classes("text-2xl font-bold")
    ui.label(f'{prediction["league"]} {prediction["season"]}').classes("fm-muted")
    with ui.column().classes("gap-4 w-full mt-2"):
        _probability_row(f'{prediction["home"]} win', prediction["home_win"], "positive")
        _probability_row("Draw", prediction["draw"], "primary")
        _probability_row(f'{prediction["away"]} win', prediction["away_win"], "warning")
    ui.separator()
    with ui.grid(columns="repeat(4, minmax(120px, 1fr))").classes("gap-3 w-full max-md:grid-cols-2"):
        _metric("Home form", f'{prediction["home_form"]}/15')
        _metric("Away form", f'{prediction["away_form"]}/15')
        _metric("Home rank", f'#{prediction["home_rank"]}')
        _metric("Away rank", f'#{prediction["away_rank"]}')
    ui.label(
        "Model inputs: last-5 form, average goals for/against, calculated standings position, and home advantage."
    ).classes("text-sm fm-muted")


def _probability_row(label: str, value: int, color: str) -> None:
    with ui.column().classes("gap-1 w-full"):
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(label).classes("font-medium")
            ui.label(f"{value}%").classes("font-bold")
        ui.linear_progress(value=value / 100).props(f"color={color} rounded").classes("h-3")


def _metric(label: str, value: str) -> None:
    with ui.column().classes("gap-0"):
        ui.label(label).classes("text-xs uppercase fm-muted")
        ui.label(value).classes("text-lg font-bold")
