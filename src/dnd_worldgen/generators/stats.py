"""Ability score rolling and modifier arithmetic.

Every function that needs randomness takes an explicit
:class:`random.Random` so results are reproducible from a seed.
"""

import random

from dnd_worldgen.config import STAT_NAMES
from dnd_worldgen.models import AbilityScore

_DICE_ROLLED = 4
_DIE_SIDES = 6


def roll_ability_score(rng: random.Random) -> int:
    """Roll 4d6 and drop the lowest die (range 3-18)."""
    rolls = sorted(rng.randint(1, _DIE_SIDES) for _ in range(_DICE_ROLLED))
    return sum(rolls[1:])


def ability_modifier(score: int) -> int:
    """Return the D&D modifier for an ability score.

    For example 8 gives -1 and 15 gives +2.
    """
    return (score - 10) // 2


def format_modifier(modifier: int) -> str:
    """Format a modifier with an explicit sign.

    For example 2 gives '+2' and 0 gives '+0'.
    """
    return f"{modifier:+d}"


def generate_abilities(rng: random.Random) -> dict[str, AbilityScore]:
    """Roll all six ability scores in the standard order.

    The order is :data:`~dnd_worldgen.config.STAT_NAMES`.
    """
    abilities: dict[str, AbilityScore] = {}
    for name in STAT_NAMES:
        score = roll_ability_score(rng)
        abilities[name] = AbilityScore(
            score=score, modifier=ability_modifier(score)
        )
    return abilities
