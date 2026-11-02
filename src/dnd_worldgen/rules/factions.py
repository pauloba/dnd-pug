"""Building blocks of faction names.

Originally extracted from the tables of the first, single-file
version of the generator (see the git history). It is now
hand-maintained: edit it directly.
"""

from typing import Final

FACTION_TYPE_IDS: Final[tuple[str, ...]] = (
    "guild",
    "cult",
    "empire",
    "rebel_syndicate",
    "circle_of_druids",
    "eco_engineers_alliance",
)

#: The two adjective pools are separate because translations differ per
#: pool.
FIRST_ADJECTIVE_IDS: Final[tuple[str, ...]] = (
    "iron",
    "golden",
    "shadowed",
    "arcane",
    "celestial",
    "verdant",
)

SECOND_ADJECTIVE_IDS: Final[tuple[str, ...]] = (
    "crimson",
    "silent",
    "boundless",
    "verdant",
    "ebon",
    "solar",
)
