"""Tests for assembling a whole universe."""

import random
import re

import pytest

from dnd_worldgen.config import MAX_PLAYERS, UNIVERSE_ID_NUMBER_RANGE
from dnd_worldgen.generators.character import generate_character
from dnd_worldgen.generators.factions import generate_factions
from dnd_worldgen.generators.story import generate_story
from dnd_worldgen.generators.universe import (
    choose_party_names,
    generate_universe,
)
from dnd_worldgen.i18n import Translator, hook_text, spells_text, story_text
from dnd_worldgen.models import Faction, GenerationOptions, Language, Universe
from dnd_worldgen.rules.themes import SETTLEMENT_IDS_BY_THEME, THEME_IDS

EN = Translator.load(Language.EN)
ES = Translator.load(Language.ES)


def make(
    seed: int = 42,
    theme_id: str = "steampunk",
    players: int = 4,
    language: Language = Language.EN,
    level: int = 1,
) -> Universe:
    options = GenerationOptions(
        theme_id=theme_id,
        language=language,
        num_players=players,
        character_level=level,
    )
    return generate_universe(
        options, random.Random(seed), Translator.load(language)
    )


# ------------------------------------------------------------ original
# values


def test_seed_42_matches_the_original_script() -> None:
    """Golden values captured from the original (English, steampunk, 4
    players).
    """
    universe = make(42)
    assert universe.universe_id == "UNI-2876"
    assert universe.theme_id == "steampunk"
    assert universe.factions == (
        Faction("eco_engineers_alliance", "iron", "crimson"),
        Faction("eco_engineers_alliance", "shadowed", "silent"),
        Faction("cult", "golden", "solar"),
    )
    assert universe.settlement_ids == (
        "cogford",
        "steam_gallow",
        "aether_spire",
    )
    assert universe.story.template_id == "story_4"
    assert [c.name for c in universe.party] == [
        "Gideon Sterling",
        "Clara Copper",
        "Baron Oswald",
        "Ada Finch",
    ]
    assert [c.class_id for c in universe.party] == [
        "warlock",
        "bard",
        "warlock",
        "rogue",
    ]


def test_eight_players_continue_the_numbering_after_the_name_pool() -> None:
    names = [c.name for c in make(42, players=8).party]
    assert names[:6] == [
        "Gideon Sterling",
        "Clara Copper",
        "Baron Oswald",
        "Ada Finch",
        "Silas Vane",
        "Vera Gearheart",
    ]
    assert names[6:] == ["Adventurer 7", "Adventurer 8"]


def test_spanish_fallback_names_are_in_spanish() -> None:
    names = [c.name for c in make(42, players=8, language=Language.ES).party]
    assert names[6:] == ["Aventurero 7", "Aventurero 8"]


# ----------------------------------------------------------------
# properties


def test_same_seed_gives_the_same_universe() -> None:
    assert make(7) == make(7)


def test_different_seeds_give_different_universes() -> None:
    assert make(1) != make(2)


def test_the_world_does_not_depend_on_the_party_size() -> None:
    """Factions, settlements and story are drawn before any
    character.
    """
    small, large = make(11, players=1), make(11, players=8)
    assert small.factions == large.factions
    assert small.settlement_ids == large.settlement_ids
    assert small.story == large.story


@pytest.mark.parametrize("players", range(1, MAX_PLAYERS + 1))
def test_party_size_and_unique_names(players: int) -> None:
    party = make(3, players=players).party
    assert len(party) == players
    assert len({c.name for c in party}) == players


def test_character_level_is_passed_to_everyone() -> None:
    assert {c.level for c in make(1, level=9).party} == {9}


def test_party_members_belong_to_the_universe() -> None:
    universe = make(5, players=6)
    for character in universe.party:
        assert character.faction in universe.factions
        assert character.settlement_id in universe.settlement_ids


def test_universe_id_format_and_range() -> None:
    low, high = UNIVERSE_ID_NUMBER_RANGE
    for seed in range(100):
        match = re.fullmatch(r"UNI-(\d{4})", make(seed, players=1).universe_id)
        assert match and low <= int(match.group(1)) <= high


def test_only_the_given_rng_is_used() -> None:
    random.seed(1)
    before = random.getstate()
    make(99)
    assert random.getstate() == before


def test_random_draws_happen_in_the_documented_order() -> None:
    universe = make(123, players=5)
    rng = random.Random(123)
    factions = generate_factions(rng)
    settlements = tuple(rng.sample(SETTLEMENT_IDS_BY_THEME["steampunk"], 3))
    story = generate_story(rng, "steampunk", factions, settlements)
    names = choose_party_names(rng, EN, "steampunk", 5)
    party = tuple(
        generate_character(
            rng,
            name=name,
            level=1,
            factions=factions,
            settlement_ids=settlements,
        )
        for name in names
    )
    low, high = UNIVERSE_ID_NUMBER_RANGE
    assert universe.factions == factions
    assert universe.settlement_ids == settlements
    assert universe.story == story
    assert universe.party == party
    assert universe.universe_id == f"UNI-{rng.randint(low, high)}"


# ---------------------------------------------------------------- name
# pool


def test_names_come_from_the_theme_pool_when_it_is_big_enough() -> None:
    pool = set(EN.strings("names.steampunk"))
    names = choose_party_names(random.Random(1), EN, "steampunk", 6)
    assert set(names) == pool and len(names) == 6


def test_fewer_players_than_names_draws_a_subset() -> None:
    names = choose_party_names(random.Random(1), ES, "steampunk", 2)
    assert len(names) == 2 and set(names) <= set(ES.strings("names.steampunk"))


# ----------------------------------------------------------------- all
# themes


@pytest.mark.parametrize("language", list(Language))
@pytest.mark.parametrize("theme_id", THEME_IDS)
def test_every_theme_generates_and_renders_in_every_language(
    theme_id: str, language: Language
) -> None:
    translator = Translator.load(language)
    for players in (1, 6, MAX_PLAYERS):
        universe = make(players, theme_id, players, language)
        assert universe.theme_id == theme_id
        assert len(universe.party) == players
        assert story_text(translator, theme_id, universe.story).strip()
        for character in universe.party:
            assert hook_text(translator, character).strip()
            assert spells_text(translator, character).strip()


# ----------------------------------------------------------------
# validation


def test_translator_language_must_match_the_options() -> None:
    options = GenerationOptions("steampunk", language=Language.ES)
    with pytest.raises(ValueError, match="does not match"):
        generate_universe(options, random.Random(1), EN)


def test_unknown_theme_is_rejected_by_the_options() -> None:
    with pytest.raises(
        ValueError, match="Unknown theme ID 'atlantis'.*steampunk"
    ):
        GenerationOptions(theme_id="atlantis")
