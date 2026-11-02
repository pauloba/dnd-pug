"""Assembly of a whole universe: world, story, encounters and party.

This module only produces data. It never prints, touches the file system
or renders anything.
"""

import random

from dnd_worldgen.config import (
    SETTLEMENT_COUNT,
    UNIVERSE_ID_NUMBER_RANGE,
    UNIVERSE_ID_PREFIX,
)
from dnd_worldgen.generators.character import generate_character
from dnd_worldgen.generators.encounters import get_encounters
from dnd_worldgen.generators.factions import generate_factions
from dnd_worldgen.generators.story import generate_story
from dnd_worldgen.i18n import Translator
from dnd_worldgen.models import GenerationOptions, Universe
from dnd_worldgen.rules.themes import SETTLEMENT_IDS_BY_THEME


def choose_party_names(
    rng: random.Random, translator: Translator, theme_id: str, count: int
) -> list[str]:
    """Draw unique names from the theme's pool.

    Players beyond the pool get a numbered fallback name.

    Each theme has 6 names. Players beyond the pool get a numbered name
    that continues the count (7, 8, ...), written in the translator's
    language.
    """
    pool = translator.strings(f"names.{theme_id}")
    names = rng.sample(pool, min(count, len(pool)))
    while len(names) < count:
        names.append(
            translator.t("party.fallback_name", number=len(names) + 1)
        )
    return names


def generate_universe(
    options: GenerationOptions, rng: random.Random, translator: Translator
) -> Universe:
    """Generate a universe for the given options.

    The random draws happen in the order the original script used
    (factions, settlements, story, party names, characters, universe
    number), so a seed still reproduces the original universe. Do not
    reorder them casually.
    """
    if translator.language is not options.language:
        raise ValueError(
            f"Translator language {translator.language.value!r} does not "
            f"match the requested language {options.language.value!r}"
        )
    theme_id = options.theme_id

    factions = generate_factions(rng)
    settlement_ids = tuple(
        rng.sample(SETTLEMENT_IDS_BY_THEME[theme_id], SETTLEMENT_COUNT)
    )
    story = generate_story(rng, theme_id, factions, settlement_ids)
    encounters = get_encounters(theme_id)

    names = choose_party_names(rng, translator, theme_id, options.num_players)
    party = tuple(
        generate_character(
            rng,
            name=name,
            level=options.character_level,
            factions=factions,
            settlement_ids=settlement_ids,
        )
        for name in names
    )

    low, high = UNIVERSE_ID_NUMBER_RANGE
    return Universe(
        universe_id=f"{UNIVERSE_ID_PREFIX}{rng.randint(low, high)}",
        theme_id=theme_id,
        factions=factions,
        settlement_ids=settlement_ids,
        story=story,
        encounters=encounters,
        party=party,
    )
