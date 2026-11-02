"""Random generation of one player character."""

import random
from collections.abc import Sequence

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


def generate_character(
    rng: random.Random,
    *,
    name: str,
    level: int,
    factions: Sequence[Faction],
    settlement_ids: Sequence[str],
) -> Character:
    """Roll a character who belongs to one of the universe's factions.

    The random draws happen in a fixed order (race, class, subclass,
    background, faction, settlement, alignment, hook, ability scores).
    It is the order the original script used, so a given seed still
    produces the same character. Do not reorder them casually.
    """
    if not factions:
        raise ValueError("generate_character needs at least one faction")
    if not settlement_ids:
        raise ValueError("generate_character needs at least one settlement")

    race_id = rng.choice(RACE_IDS)
    class_id = rng.choice(CLASS_IDS)
    subclass_id = rng.choice(SUBCLASS_IDS_BY_CLASS[class_id])
    background_id = rng.choice(BACKGROUND_IDS)
    faction = rng.choice(factions)
    settlement_id = rng.choice(settlement_ids)
    alignment_id = rng.choice(ALIGNMENT_IDS)
    hook_id = rng.choice(HOOK_IDS)
    abilities = generate_abilities(rng)

    return Character(
        name=name,
        race_id=race_id,
        class_id=class_id,
        subclass_id=subclass_id,
        background_id=background_id,
        alignment_id=alignment_id,
        level=level,
        faction=faction,
        settlement_id=settlement_id,
        hook_id=hook_id,
        abilities=abilities,
        combat=build_combat_profile(class_id, abilities),
    )
