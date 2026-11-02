"""Tests for the domain models and option validation."""

import re
from dataclasses import FrozenInstanceError

import pytest

from dnd_worldgen.config import (
    DEFAULT_LEVEL,
    DEFAULT_PLAYERS,
    MAX_LEVEL,
    MAX_PLAYERS,
    MIN_LEVEL,
    MIN_PLAYERS,
)
from dnd_worldgen.models import (
    AbilityScore,
    Encounter,
    EncounterSet,
    EncounterStage,
    GenerationOptions,
    Language,
)


def test_options_defaults() -> None:
    options = GenerationOptions(theme_id="steampunk")
    assert options.language is Language.EN
    assert options.num_players == DEFAULT_PLAYERS
    assert options.character_level == DEFAULT_LEVEL
    assert options.seed is None


@pytest.mark.parametrize(
    "players", [MIN_PLAYERS, DEFAULT_PLAYERS, MAX_PLAYERS]
)
def test_options_accept_valid_player_counts(players: int) -> None:
    assert (
        GenerationOptions("steampunk", num_players=players).num_players
        == players
    )


@pytest.mark.parametrize("players", [MIN_PLAYERS - 1, MAX_PLAYERS + 1, -3])
def test_options_reject_invalid_player_counts(players: int) -> None:
    with pytest.raises(ValueError, match="num_players"):
        GenerationOptions("steampunk", num_players=players)


@pytest.mark.parametrize("level", [MIN_LEVEL, 5, MAX_LEVEL])
def test_options_accept_valid_levels(level: int) -> None:
    assert (
        GenerationOptions("steampunk", character_level=level).character_level
        == level
    )


@pytest.mark.parametrize("level", [MIN_LEVEL - 1, MAX_LEVEL + 1])
def test_options_reject_invalid_levels(level: int) -> None:
    with pytest.raises(ValueError, match="character_level"):
        GenerationOptions("steampunk", character_level=level)


def test_models_are_frozen() -> None:
    score = AbilityScore(score=10, modifier=0)
    with pytest.raises(FrozenInstanceError):
        score.score = 18  # type: ignore[misc]


def test_language_values_are_locale_codes() -> None:
    values = {language.value for language in Language}
    assert {"en", "es"} <= values
    assert all(re.fullmatch(r"[a-z]{2}", value) for value in values)
    assert Language("es") is Language.ES


def test_encounter_set_stages_in_play_order() -> None:
    low = Encounter(EncounterStage.LOW, "loc_low", ("a",))
    mid = Encounter(EncounterStage.MID, "loc_mid", ("b",))
    boss = Encounter(
        EncounterStage.BOSS, "loc_boss", ("c",), unlock_id="unlock"
    )
    stages = EncounterSet(low=low, mid=mid, boss=boss).stages
    assert [e.stage for e in stages] == [
        EncounterStage.LOW,
        EncounterStage.MID,
        EncounterStage.BOSS,
    ]
    assert stages[2].unlock_id == "unlock"
    assert low.unlock_id is None


def test_options_reject_unknown_themes() -> None:
    with pytest.raises(ValueError, match="Unknown theme ID 'atlantis'"):
        GenerationOptions(theme_id="atlantis")
