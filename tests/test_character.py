"""Tests for random character generation."""

import random
from collections.abc import Sequence

import pytest

from dnd_worldgen.generators.character import generate_character
from dnd_worldgen.generators.combat import build_combat_profile
from dnd_worldgen.generators.stats import generate_abilities
from dnd_worldgen.models import Character, Faction
from dnd_worldgen.rules.characters import (
    ALIGNMENT_IDS,
    BACKGROUND_IDS,
    CLASS_IDS,
    HOOK_IDS,
    RACE_IDS,
    SUBCLASS_IDS_BY_CLASS,
)
from dnd_worldgen.rules.themes import SETTLEMENT_IDS_BY_THEME, THEME_IDS

FACTIONS = (
    Faction("guild", "iron", "crimson"),
    Faction("cult", "golden", "silent"),
    Faction("circle_of_druids", "verdant", "verdant"),
)
SETTLEMENTS = SETTLEMENT_IDS_BY_THEME[THEME_IDS[0]][:3]


def make(
    seed: int,
    *,
    name: str = "Test Hero",
    level: int = 1,
    factions: Sequence[Faction] = FACTIONS,
    settlement_ids: Sequence[str] = SETTLEMENTS,
) -> Character:
    return generate_character(
        random.Random(seed),
        name=name,
        level=level,
        factions=factions,
        settlement_ids=settlement_ids,
    )


def test_seed_42_matches_the_original_script() -> None:
    """Golden values from the original character loop (seed 42)."""
    c = make(42)
    assert (c.race_id, c.class_id, c.subclass_id) == (
        "elf",
        "fighter",
        "eldritch_knight",
    )
    assert (c.background_id, c.alignment_id, c.hook_id) == (
        "sage",
        "chaotic_good",
        "hook_1",
    )
    assert c.faction == FACTIONS[0]
    assert c.settlement_id == "cogford"
    assert {n: (a.score, a.modifier) for n, a in c.abilities.items()} == {
        "STR": (17, 3),
        "DEX": (10, 0),
        "CON": (9, -1),
        "INT": (12, 1),
        "WIS": (18, 4),
        "CHA": (13, 1),
    }
    assert (c.combat.hp, c.combat.armor_class, c.combat.armor_id) == (
        9,
        16,
        "chain_mail",
    )


def test_seed_7_matches_the_original_script() -> None:
    """Golden values from the original character loop (seed 7, negative
    DEX).
    """
    c = make(7)
    assert (c.race_id, c.class_id, c.subclass_id) == (
        "dragonborn",
        "rogue",
        "assassin",
    )
    assert (c.background_id, c.alignment_id, c.hook_id) == (
        "acolyte",
        "neutral_good",
        "hook_3",
    )
    assert c.settlement_id == "aether_spire"
    assert (c.combat.hp, c.combat.armor_class, c.combat.initiative) == (
        7,
        10,
        -1,
    )


def test_random_draws_happen_in_the_documented_order() -> None:
    c = make(123)
    rng = random.Random(123)
    race = rng.choice(RACE_IDS)
    class_id = rng.choice(CLASS_IDS)
    subclass = rng.choice(SUBCLASS_IDS_BY_CLASS[class_id])
    background = rng.choice(BACKGROUND_IDS)
    faction = rng.choice(FACTIONS)
    settlement = rng.choice(SETTLEMENTS)
    alignment = rng.choice(ALIGNMENT_IDS)
    hook = rng.choice(HOOK_IDS)
    abilities = generate_abilities(rng)
    assert (c.race_id, c.class_id, c.subclass_id, c.background_id) == (
        race,
        class_id,
        subclass,
        background,
    )
    assert (c.faction, c.settlement_id, c.alignment_id, c.hook_id) == (
        faction,
        settlement,
        alignment,
        hook,
    )
    assert c.abilities == abilities


def test_same_seed_gives_the_same_character() -> None:
    assert make(5) == make(5)


def test_different_seeds_give_different_characters() -> None:
    assert make(1) != make(2)


def test_name_and_level_are_passed_through() -> None:
    c = make(1, name="Gideon", level=7)
    assert (c.name, c.level) == ("Gideon", 7)


def test_only_the_given_rng_is_used() -> None:
    random.seed(1)
    before = random.getstate()
    make(99)
    assert random.getstate() == before


def test_character_needs_at_least_one_faction_and_settlement() -> None:
    with pytest.raises(ValueError, match="faction"):
        make(1, factions=())
    with pytest.raises(ValueError, match="settlement"):
        make(1, settlement_ids=())


def test_500_characters_are_valid_and_cover_every_option() -> None:
    seen: dict[str, set[str]] = {
        key: set()
        for key in ("race", "class", "background", "alignment", "hook")
    }
    for seed in range(500):
        c = make(seed)
        assert c.subclass_id in SUBCLASS_IDS_BY_CLASS[c.class_id]
        assert c.faction in FACTIONS
        assert c.settlement_id in SETTLEMENTS
        assert c.combat.hp >= 1
        assert c.combat == build_combat_profile(c.class_id, c.abilities)
        seen["race"].add(c.race_id)
        seen["class"].add(c.class_id)
        seen["background"].add(c.background_id)
        seen["alignment"].add(c.alignment_id)
        seen["hook"].add(c.hook_id)
    assert seen["race"] == set(RACE_IDS)
    assert seen["class"] == set(CLASS_IDS)
    assert seen["background"] == set(BACKGROUND_IDS)
    assert seen["alignment"] == set(ALIGNMENT_IDS)
    assert seen["hook"] == set(HOOK_IDS)
