"""Random generation of a universe's factions."""

import random

from dnd_worldgen.config import FACTION_COUNT
from dnd_worldgen.models import Faction
from dnd_worldgen.rules.factions import (
    FACTION_TYPE_IDS,
    FIRST_ADJECTIVE_IDS,
    SECOND_ADJECTIVE_IDS,
)


def generate_faction(rng: random.Random) -> Faction:
    """Roll one faction: its type, then its two adjectives."""
    type_id = rng.choice(FACTION_TYPE_IDS)
    first_adjective_id = rng.choice(FIRST_ADJECTIVE_IDS)
    second_adjective_id = rng.choice(SECOND_ADJECTIVE_IDS)
    return Faction(type_id, first_adjective_id, second_adjective_id)


def generate_factions(
    rng: random.Random, count: int = FACTION_COUNT
) -> tuple[Faction, ...]:
    """Roll ``count`` factions (duplicates are possible).

    This matches the original script.
    """
    return tuple(generate_faction(rng) for _ in range(count))
