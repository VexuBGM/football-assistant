import math
from dataclasses import dataclass

from .features import PredictionFeatures, build_prediction_features

HOME_ADVANTAGE = 0.08


@dataclass(frozen=True)
class MatchPrediction:
    league_name: str
    season: str
    home_team: str
    away_team: str
    home_win: int
    draw: int
    away_win: int
    features: PredictionFeatures

    @property
    def total_probability(self) -> int:
        return self.home_win + self.draw + self.away_win


def predict_match(home_team: str, away_team: str) -> tuple[MatchPrediction | None, str | None]:
    features, error = build_prediction_features(home_team, away_team)
    if error is not None or features is None:
        return None, error

    home_strength = features.home.strength_index + HOME_ADVANTAGE
    away_strength = features.away.strength_index
    difference = home_strength - away_strength

    draw_probability = _clamp(0.32 - abs(difference) * 0.12, 0.18, 0.34)
    remaining = 1 - draw_probability
    home_share = 1 / (1 + math.exp(-3.0 * difference))
    raw_probabilities = [
        remaining * home_share,
        draw_probability,
        remaining * (1 - home_share),
    ]
    home_win, draw, away_win = _round_percentages(raw_probabilities)

    return (
        MatchPrediction(
            league_name=features.league_name,
            season=features.season,
            home_team=features.home.name,
            away_team=features.away.name,
            home_win=home_win,
            draw=draw,
            away_win=away_win,
            features=features,
        ),
        None,
    )


def format_prediction(home_team: str, away_team: str) -> str:
    prediction, error = predict_match(home_team, away_team)
    if error is not None or prediction is None:
        return error or "Неуспешна прогноза."

    return "\n".join(
        [
            (
                f'Прогноза за {prediction.home_team} срещу {prediction.away_team} '
                f'({prediction.league_name} {prediction.season}):'
            ),
            f"Победа {prediction.home_team}: {prediction.home_win}%",
            f"Равен: {prediction.draw}%",
            f"Победа {prediction.away_team}: {prediction.away_win}%",
            (
                "Модел: последни 5 мача, средни GF/GA, текущо класиране "
                "и домакински бонус."
            ),
        ]
    )


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _round_percentages(probabilities: list[float]) -> tuple[int, int, int]:
    scaled = [probability * 100 for probability in probabilities]
    rounded = [math.floor(value) for value in scaled]
    missing = 100 - sum(rounded)
    remainders = sorted(
        enumerate(value - rounded[index] for index, value in enumerate(scaled)),
        key=lambda item: item[1],
        reverse=True,
    )
    for index, _ in remainders[:missing]:
        rounded[index] += 1
    return rounded[0], rounded[1], rounded[2]
