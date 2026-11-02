"""Character building blocks: races, classes, subclasses and more.

Originally extracted from the tables of the first, single-file
version of the generator (see the git history). It is now
hand-maintained: edit it directly.
"""

from collections.abc import Mapping
from typing import Final

RACE_IDS: Final[tuple[str, ...]] = (
    "human",
    "elf",
    "dwarf",
    "halfling",
    "tiefling",
    "dragonborn",
    "gnome",
    "half_orc",
)

CLASS_IDS: Final[tuple[str, ...]] = (
    "fighter",
    "wizard",
    "rogue",
    "cleric",
    "ranger",
    "paladin",
    "bard",
    "druid",
    "warlock",
)

SUBCLASS_IDS_BY_CLASS: Final[Mapping[str, tuple[str, ...]]] = {
    "fighter": (
        "champion",
        "battle_master",
        "eldritch_knight",
    ),
    "wizard": (
        "school_of_evocation",
        "school_of_abjuration",
        "school_of_divination",
    ),
    "rogue": (
        "thief",
        "assassin",
        "arcane_trickster",
    ),
    "cleric": (
        "life_domain",
        "light_domain",
        "war_domain",
    ),
    "ranger": (
        "hunter",
        "beast_master",
        "gloom_stalker",
    ),
    "paladin": (
        "oath_of_devotion",
        "oath_of_the_ancients",
        "oath_of_vengeance",
    ),
    "bard": (
        "college_of_lore",
        "college_of_valor",
        "college_of_glamour",
    ),
    "druid": (
        "circle_of_the_land",
        "circle_of_the_moon",
        "circle_of_stars",
    ),
    "warlock": (
        "the_fiend",
        "the_great_old_one",
        "the_archfey",
    ),
}

BACKGROUND_IDS: Final[tuple[str, ...]] = (
    "acolyte",
    "criminal",
    "folk_hero",
    "noble",
    "sage",
    "soldier",
    "urchin",
    "outlander",
)

ALIGNMENT_IDS: Final[tuple[str, ...]] = (
    "lawful_good",
    "neutral_good",
    "chaotic_good",
    "lawful_neutral",
    "true_neutral",
    "chaotic_neutral",
    "lawful_evil",
    "neutral_evil",
    "chaotic_evil",
)

#: Story hooks. Their text may use ``{faction}`` and ``{settlement}``.
HOOK_IDS: Final[tuple[str, ...]] = (
    "hook_1",
    "hook_2",
    "hook_3",
    "hook_4",
)
