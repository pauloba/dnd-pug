"""Project-wide constants and defaults.

Anything a user can tune (limits, defaults) lives here so that the CLI,
validation and tests all read the same values.
"""

from typing import Final

#: The six ability scores, in the order they are rolled and displayed.
STAT_NAMES: Final[tuple[str, ...]] = ("STR", "DEX", "CON", "INT", "WIS", "CHA")

#: Number of player characters per generated universe.
MIN_PLAYERS: Final = 1
MAX_PLAYERS: Final = 8
DEFAULT_PLAYERS: Final = 4

#: Character level range (D&D 5e levels run from 1 to 20).
MIN_LEVEL: Final = 1
MAX_LEVEL: Final = 20
DEFAULT_LEVEL: Final = 1

#: Size of a generated world (fixed in the original generator).
FACTION_COUNT: Final = 3
SETTLEMENT_COUNT: Final = 3

#: Universe IDs look like "UNI-4821".
UNIVERSE_ID_PREFIX: Final = "UNI-"
UNIVERSE_ID_NUMBER_RANGE: Final = (1000, 9999)
