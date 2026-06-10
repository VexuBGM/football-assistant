from nicegui import ui

from .. import adapters
from ..layout import page_shell, section
from ..notifications import notify_and_log


@ui.page("/prediction")
def prediction_page() -> None:
    def content() -> None:
        result_holder = ui.column().classes("gap-3 w-full")

        def render_prediction() -> None:
            result_holder.clear()
            prediction, error = adapters.prediction_view(home.value or "", away.value or "")
            with result_holder:
                if error or prediction is None:
                    ui.label(error or "Prediction failed.").classes("text-negative font-medium")
                    return
                ui.label(f'{prediction["home"]} vs {prediction["away"]}').classes("text-2xl font-bold")
                ui.label(f'{prediction["league"]} {prediction["season"]}').classes("fm-muted")
                for label, value, color in [
                    (f'{prediction["home"]} win', prediction["home_win"], "#15803d"),
                    ("Draw", prediction["draw"], "#2563eb"),
                    (f'{prediction["away"]} win', prediction["away_win"], "#b45309"),
                ]:
                    ui.label(f"{label}: {value}%").classes("font-medium")
                    ui.linear_progress(value / 100, color=color).classes("h-3 rounded")
                ui.separator()
                ui.label(
                    "Model inputs: last-5 form, average goals for/against, calculated standings position, and home advantage."
                ).classes("fm-muted")
                ui.label(
                    f'Form points: {prediction["home"]} {prediction["home_form"]}, '
                    f'{prediction["away"]} {prediction["away_form"]}. '
                    f'Ranks: {prediction["home_rank"]} and {prediction["away_rank"]}.'
                ).classes("text-sm")

        def predict() -> None:
            prediction, error = adapters.prediction_view(home.value or "", away.value or "")
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
            render_prediction()

        with ui.grid(columns="1fr 1.4fr").classes("gap-4 w-full max-lg:grid-cols-1"):
            with section("Prediction Input", "Both teams must share a league and have enough played matches"):
                home = ui.select(adapters.club_options(), label="Home team").props("outlined").classes("w-full")
                away = ui.select(adapters.club_options(), label="Away team").props("outlined").classes("w-full")
                ui.button("Predict", icon="insights", on_click=predict)
            with section("Probabilities", "Rule-based prediction from real match data"):
                result_holder

    page_shell("/prediction", "AI Prediction", "Estimate home win, draw, and away win probabilities.", content)
