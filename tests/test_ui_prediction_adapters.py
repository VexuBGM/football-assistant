from src.ui import adapters
from src.services import seed_service


class TestPredictionAdapters:
    def test_prediction_league_options_include_seeded_played_league(self):
        seed_service.seed_full_demo_data()

        options = adapters.prediction_league_options()

        assert f"{seed_service.DEMO_LEAGUE} | {seed_service.DEMO_SEASON}" in options
        assert f"{seed_service.SANDBOX_LEAGUE} | {seed_service.SANDBOX_SEASON}" not in options

    def test_suggested_prediction_pair_can_calculate_prediction(self):
        seed_service.seed_full_demo_data()

        home, away = adapters.suggested_prediction_pair(seed_service.DEMO_LEAGUE, seed_service.DEMO_SEASON)
        prediction, error = adapters.prediction_view(home or "", away or "")

        assert home is not None
        assert away is not None
        assert error is None
        assert prediction is not None
        assert prediction["home_win"] + prediction["draw"] + prediction["away_win"] == 100

    def test_club_options_for_league_are_limited_to_that_league(self):
        seed_service.seed_full_demo_data()

        options = adapters.club_options_for_league(seed_service.DEMO_LEAGUE, seed_service.DEMO_SEASON)

        assert "Levski Sofia" in options
        assert "CSKA Sofia" in options
        assert len(options) == 6
