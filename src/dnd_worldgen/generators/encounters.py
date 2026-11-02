"""The threat dossier of a theme."""

from dnd_worldgen.models import EncounterSet
from dnd_worldgen.rules.encounters import ENCOUNTERS_BY_THEME
from dnd_worldgen.rules.themes import require_theme


def get_encounters(theme_id: str) -> EncounterSet:
    """Return the theme's low, mid and boss encounters.

    The dossier is fixed per theme (no randomness, as in the original).
    An unknown theme raises ``ValueError``; the original silently used
    the first theme instead.
    """
    return ENCOUNTERS_BY_THEME[require_theme(theme_id)]
