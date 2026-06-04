from dataclasses import dataclass


@dataclass
class UiState:
    league_name: str | None = None
    season: str | None = None
    match_id: int | None = None


state = UiState()
