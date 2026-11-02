"""Tests for combat arithmetic and the class rules table."""

import re

import pytest

from dnd_worldgen.generators.combat import (
    build_combat_profile,
    compute_armor_class,
    compute_hit_points,
    compute_initiative,
    get_class_rules,
)
from dnd_worldgen.models import AbilityScore
from dnd_worldgen.rules.characters import CLASS_IDS
from dnd_worldgen.rules.classes import CLASSES, PROFICIENCY_BONUS, ClassRules

LIGHT = ClassRules(
    hit_die=8, armor_id="x", base_armor_class=11, adds_dexterity=True
)
HEAVY = ClassRules(
    hit_die=10, armor_id="x", base_armor_class=16, adds_dexterity=False
)


def abilities(con: int = 0, dex: int = 0) -> dict[str, AbilityScore]:
    """Six ability scores where only CON and DEX modifiers matter."""
    scores = {
        name: AbilityScore(10, 0) for name in ("STR", "INT", "WIS", "CHA")
    }
    scores["CON"] = AbilityScore(10 + 2 * con, con)
    scores["DEX"] = AbilityScore(10 + 2 * dex, dex)
    return scores


@pytest.mark.parametrize(
    ("hit_die", "con", "expected"),
    [
        (10, 0, 10),
        (10, 4, 14),
        (10, -1, 9),
        (6, -1, 5),
        (6, -5, 1),
        (6, -10, 1),
    ],
)
def test_hit_points_never_drop_below_one(
    hit_die: int, con: int, expected: int
) -> None:
    rules = ClassRules(hit_die, "x", 10, True)
    assert compute_hit_points(rules, con) == expected


@pytest.mark.parametrize("dex", [-2, 0, 3])
def test_heavy_armor_ignores_dexterity(dex: int) -> None:
    assert compute_armor_class(HEAVY, dex) == 16


@pytest.mark.parametrize(
    ("dex", "expected"), [(3, 14), (0, 11), (-1, 10), (-3, 8)]
)
def test_light_armor_adds_dexterity_even_when_negative(
    dex: int, expected: int
) -> None:
    assert compute_armor_class(LIGHT, dex) == expected


@pytest.mark.parametrize("dex", [-3, 0, 4])
def test_initiative_equals_dexterity_modifier(dex: int) -> None:
    assert compute_initiative(dex) == dex


def test_profile_for_a_fighter_matches_the_original() -> None:
    """Golden values from the original script (seed 42: CON -1, DEX
    +0).
    """
    profile = build_combat_profile("fighter", abilities(con=-1, dex=0))
    assert (profile.hp, profile.armor_class, profile.initiative) == (9, 16, 0)
    assert profile.proficiency == PROFICIENCY_BONUS == 2
    assert profile.armor_id == "chain_mail"


def test_profile_for_a_rogue_matches_the_original() -> None:
    """Golden values from the original script (seed 7: CON -1, DEX
    -1).
    """
    profile = build_combat_profile("rogue", abilities(con=-1, dex=-1))
    assert (profile.hp, profile.armor_class, profile.initiative) == (7, 10, -1)
    assert profile.armor_id == "leather_armor"


def test_every_class_has_rules_in_menu_order() -> None:
    assert tuple(CLASSES) == CLASS_IDS


@pytest.mark.parametrize("class_id", CLASS_IDS)
def test_class_rules_are_sensible(class_id: str) -> None:
    rules = get_class_rules(class_id)
    assert rules.hit_die in (6, 8, 10, 12)
    assert 10 <= rules.base_armor_class <= 18
    assert re.fullmatch(r"[a-z0-9_]+", rules.armor_id)


def test_light_armor_classes_share_leather_armor() -> None:
    """The original gave rogue, bard and warlock the same armor."""
    shared = {CLASSES[c].armor_id for c in ("rogue", "bard", "warlock")}
    assert shared == {"leather_armor"}


def test_unknown_class_fails_loudly() -> None:
    with pytest.raises(
        ValueError, match=r"Unknown class ID 'jester'.*fighter"
    ):
        get_class_rules("jester")
    with pytest.raises(ValueError, match="Unknown class ID"):
        build_combat_profile("jester", abilities())
