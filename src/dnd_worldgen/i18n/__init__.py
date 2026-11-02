"""Internationalisation: locale files and the translator.

The :class:`Translator` reads the locale files.
"""

from dnd_worldgen.i18n.display import (
    armor_name,
    faction_name,
    hook_text,
    main_attack_text,
    spells_text,
    starting_equipment_text,
    story_text,
)
from dnd_worldgen.i18n.translator import (
    TranslationError,
    Translator,
    load_catalog,
)

__all__ = [
    "TranslationError",
    "Translator",
    "armor_name",
    "faction_name",
    "hook_text",
    "load_catalog",
    "main_attack_text",
    "spells_text",
    "starting_equipment_text",
    "story_text",
]
