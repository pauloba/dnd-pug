"""Which skills are governed by which ability score.

Originally extracted from the tables of the first, single-file
version of the generator (see the git history). It is now
hand-maintained: edit it directly.
"""

from collections.abc import Mapping
from typing import Final

SKILL_IDS_BY_ATTRIBUTE: Final[Mapping[str, tuple[str, ...]]] = {
    "STR": ("athletics",),
    "DEX": (
        "acrobatics",
        "sleight_of_hand",
        "stealth",
    ),
    "CON": (),
    "INT": (
        "arcana",
        "history",
        "investigation",
        "nature",
        "religion",
    ),
    "WIS": (
        "animal_handling",
        "insight",
        "medicine",
        "perception",
        "survival",
    ),
    "CHA": (
        "deception",
        "intimidation",
        "performance",
        "persuasion",
    ),
}
