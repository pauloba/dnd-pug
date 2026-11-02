"""Domain models for generated universes and characters.

Design rules:

* Models are frozen dataclasses: generated data is never mutated
  afterwards.
* Models hold **stable IDs and numbers**, not translated text. A class
  is ``"fighter"``, never ``"Fighter"`` or ``"Guerrero"``. Text is
  looked up through the translator at render time, so one ``Universe``
  can be rendered in any language.
* The one deliberate exception is ``Character.name``: a proper noun
  resolved at generation time (the "Adventurer N" fallback is
  synthesised, so it has no fixed ID).
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

from dnd_worldgen.config import (
    DEFAULT_LEVEL,
    DEFAULT_PLAYERS,
    MAX_LEVEL,
    MAX_PLAYERS,
    MIN_LEVEL,
    MIN_PLAYERS,
)
from dnd_worldgen.rules.themes import require_theme


class Language(str, Enum):
    """Supported output languages.

    The value is the locale directory name.
    """

    EN = "en"
    ES = "es"


class EncounterStage(str, Enum):
    """Difficulty stages of the encounter dossier, in play order."""

    LOW = "low"
    MID = "mid"
    BOSS = "boss"


@dataclass(frozen=True)
class AbilityScore:
    """One ability score and its derived modifier.

    Both are plain integers.
    """

    score: int
    modifier: int


@dataclass(frozen=True)
class Faction:
    """A faction, identified by the parts its name is built from.

    The display name is assembled per language at render time, because
    word order differs ("The Iron Crimson Guild" vs "Gremio Hierro
    Carmesi").
    """

    type_id: str
    first_adjective_id: str
    second_adjective_id: str


@dataclass(frozen=True)
class CombatProfile:
    """Numeric combat statistics of a character.

    Attack, equipment and spell texts are not stored: they are looked up
    from the class, subclass, race and background IDs when rendering.
    """

    hp: int
    armor_class: int
    initiative: int
    proficiency: int
    armor_id: str


@dataclass(frozen=True)
class Character:
    """A generated player character."""

    name: str
    race_id: str
    class_id: str
    subclass_id: str
    background_id: str
    alignment_id: str
    level: int
    faction: Faction
    settlement_id: str
    hook_id: str
    abilities: Mapping[str, AbilityScore]
    combat: CombatProfile


@dataclass(frozen=True)
class Encounter:
    """One stage of the encounter dossier.

    All ``*_id`` values are keys into the locale files.
    """

    stage: EncounterStage
    location_id: str
    enemy_ids: tuple[str, ...]
    unlock_id: str | None = None  # only the boss encounter unlocks something


@dataclass(frozen=True)
class EncounterSet:
    """The low, mid and boss encounters of a universe."""

    low: Encounter
    mid: Encounter
    boss: Encounter

    @property
    def stages(self) -> tuple[Encounter, Encounter, Encounter]:
        """The encounters in play order."""
        return (self.low, self.mid, self.boss)


@dataclass(frozen=True)
class Story:
    """The campaign's opening conflict.

    ``template_id`` selects a story template in the locale files; the
    factions and settlements fill its placeholders when rendering.
    """

    template_id: str
    faction_a: Faction
    faction_b: Faction
    primary_settlement_id: str
    secondary_settlement_id: str


@dataclass(frozen=True)
class Universe:
    """Everything generated for one game.

    World, story, encounters and party.
    """

    universe_id: str
    theme_id: str
    factions: tuple[Faction, ...]
    settlement_ids: tuple[str, ...]
    story: Story
    encounters: EncounterSet
    party: tuple[Character, ...]


@dataclass(frozen=True)
class GenerationOptions:
    """Validated user input for one generation run."""

    theme_id: str
    language: Language = Language.EN
    num_players: int = DEFAULT_PLAYERS
    character_level: int = DEFAULT_LEVEL
    seed: int | None = None

    def __post_init__(self) -> None:
        """Reject an unknown theme or out-of-range numbers.

        Applies to the theme, the player count and the level.
        """
        require_theme(self.theme_id)
        if not MIN_PLAYERS <= self.num_players <= MAX_PLAYERS:
            raise ValueError(
                f"num_players must be between {MIN_PLAYERS} and "
                f"{MAX_PLAYERS}, got {self.num_players}"
            )
        if not MIN_LEVEL <= self.character_level <= MAX_LEVEL:
            raise ValueError(
                f"character_level must be between {MIN_LEVEL} and "
                f"{MAX_LEVEL}, got {self.character_level}"
            )
