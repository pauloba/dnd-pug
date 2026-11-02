"""Tests for ability score rolling and modifier arithmetic."""

import random
from collections.abc import Sequence

import pytest

from dnd_worldgen.config import STAT_NAMES
from dnd_worldgen.generators.stats import (
    ability_modifier,
    format_modifier,
    generate_abilities,
    roll_ability_score,
)


class ScriptedRandom(random.Random):
    """A Random whose ``randint`` returns a fixed sequence of dice."""

    def __new__(cls, dice: Sequence[int]) -> "ScriptedRandom":
        # Before Python 3.11 ``Random.__new__`` used its argument as a
        # seed, which fails for a list of dice. Create it without one.
        return super().__new__(cls)

    def __init__(self, dice: Sequence[int]) -> None:
        super().__init__()
        self._dice = iter(dice)

    def randint(self, a: int, b: int) -> int:
        return next(self._dice)


@pytest.mark.parametrize(
    ("score", "modifier"),
    [
        (1, -5),
        (3, -4),
        (8, -1),
        (9, -1),
        (10, 0),
        (11, 0),
        (12, 1),
        (15, 2),
        (20, 5),
    ],
)
def test_ability_modifier(score: int, modifier: int) -> None:
    assert ability_modifier(score) == modifier


@pytest.mark.parametrize(
    ("modifier", "text"),
    [(5, "+5"), (2, "+2"), (0, "+0"), (-1, "-1"), (-4, "-4")],
)
def test_format_modifier(modifier: int, text: str) -> None:
    assert format_modifier(modifier) == text


@pytest.mark.parametrize(
    ("dice", "expected"),
    [
        ([6, 6, 6, 6], 18),  # best case
        ([1, 1, 1, 1], 3),  # worst case
        ([1, 6, 6, 6], 18),  # the 1 is dropped
        ([2, 3, 4, 5], 12),  # the 2 is dropped
        ([5, 2, 4, 3], 12),  # order does not matter
    ],
)
def test_roll_drops_lowest_die(dice: list[int], expected: int) -> None:
    assert roll_ability_score(ScriptedRandom(dice)) == expected


def test_roll_stays_in_range() -> None:
    rng = random.Random(0)
    scores = [roll_ability_score(rng) for _ in range(2000)]
    assert min(scores) >= 3
    assert max(scores) <= 18


def test_generate_abilities_has_all_stats_in_order() -> None:
    abilities = generate_abilities(random.Random(1))
    assert tuple(abilities) == STAT_NAMES


def test_generate_abilities_modifiers_match_scores() -> None:
    for ability in generate_abilities(random.Random(2)).values():
        assert ability.modifier == ability_modifier(ability.score)


def test_same_seed_gives_same_abilities() -> None:
    assert generate_abilities(random.Random(99)) == generate_abilities(
        random.Random(99)
    )


def test_different_seeds_usually_differ() -> None:
    assert generate_abilities(random.Random(1)) != generate_abilities(
        random.Random(2)
    )


def test_matches_original_script_for_seed_42() -> None:
    """Golden values produced by the original generate_stats() with seed
    42.
    """
    abilities = generate_abilities(random.Random(42))
    actual = {
        name: (a.score, format_modifier(a.modifier))
        for name, a in abilities.items()
    }
    assert actual == {
        "STR": (13, "+1"),
        "DEX": (7, "-2"),
        "CON": (18, "+4"),
        "INT": (14, "+2"),
        "WIS": (4, "-3"),
        "CHA": (12, "+1"),
    }
