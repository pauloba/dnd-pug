"""View models: what a template needs, as display text.

Templates only loop and print. All decisions about *what* to show (which
text, which language, whether a field appears at all) are made here,
where they can be tested without rendering any HTML.
"""

from dataclasses import dataclass

from dnd_worldgen.i18n import (
    Translator,
    armor_name,
    faction_name,
    hook_text,
    main_attack_text,
    spells_text,
    starting_equipment_text,
    story_text,
)
from dnd_worldgen.models import Character, Encounter, Universe
from dnd_worldgen.rules.attributes import SKILL_IDS_BY_ATTRIBUTE

#: The sheet shows a separate "Subclass" field from this level on (as
#: the original did).
SUBCLASS_FIELD_MIN_LEVEL = 3


@dataclass(frozen=True)
class StatView:
    """One ability score box of the character sheet.

    The modifier stays a number (see the ``signed`` filter).
    """

    attribute: str  # "STR"
    label: str  # "Strength"
    score: int
    modifier: int
    skills: tuple[str, ...]


@dataclass(frozen=True)
class CharacterView:
    """A character as text, for the sheet and the party list."""

    name: str
    race: str
    class_name: str
    subclass: str
    level: int
    background: str
    faction: str
    alignment: str
    hook: str
    race_description: str
    class_description: str
    subclass_description: str
    background_description: str
    alignment_description: str
    stats: tuple[StatView, ...]
    hit_points: int
    armor_class: int
    initiative: int
    proficiency: int
    armor: str
    main_attack: str
    starting_equipment: str
    spells: str

    @property
    def shows_subclass_field(self) -> bool:
        """Whether the sheet lists the subclass as a separate field."""
        return self.level >= SUBCLASS_FIELD_MIN_LEVEL


@dataclass(frozen=True)
class EnemyView:
    """One enemy of an encounter, with the loot it carries."""

    name: str
    type: str
    armour: str
    goodies: str


@dataclass(frozen=True)
class EncounterView:
    """One stage of the encounter dossier."""

    stage: str  # "low", "mid" or "boss": also used for the CSS classes
    label: str  # e.g. "Low-level battle"
    location: str
    enemies: tuple[EnemyView, ...]
    unlock: str | None  # only the boss encounter unlocks something


@dataclass(frozen=True)
class UniverseView:
    """A whole universe as text, ready for the universe manual."""

    universe_id: str
    theme: str
    factions: tuple[str, ...]
    settlements: tuple[str, ...]
    conflict: str
    encounters: tuple[EncounterView, ...]
    party: tuple[CharacterView, ...]


def build_stat_views(
    translator: Translator, character: Character
) -> tuple[StatView, ...]:
    """Build the six ability boxes of a character sheet."""
    return tuple(
        StatView(
            attribute=attribute,
            label=translator.t(f"labels.{attribute.lower()}"),
            score=ability.score,
            modifier=ability.modifier,
            skills=tuple(
                translator.name("skills", skill_id)
                for skill_id in SKILL_IDS_BY_ATTRIBUTE[attribute]
            ),
        )
        for attribute, ability in character.abilities.items()
    )


def build_character_view(
    translator: Translator, character: Character
) -> CharacterView:
    """Turn a :class:`Character` into display text in one language."""
    combat = character.combat
    return CharacterView(
        name=character.name,
        race=translator.name("races", character.race_id),
        class_name=translator.name("classes", character.class_id),
        subclass=translator.name("subclasses", character.subclass_id),
        level=character.level,
        background=translator.name("backgrounds", character.background_id),
        faction=faction_name(translator, character.faction),
        alignment=translator.name("alignments", character.alignment_id),
        hook=hook_text(translator, character),
        race_description=translator.description("races", character.race_id),
        class_description=translator.description(
            "classes", character.class_id
        ),
        subclass_description=translator.description(
            "subclasses", character.subclass_id
        ),
        background_description=translator.description(
            "backgrounds", character.background_id
        ),
        alignment_description=translator.description(
            "alignments", character.alignment_id
        ),
        stats=build_stat_views(translator, character),
        hit_points=combat.hp,
        armor_class=combat.armor_class,
        initiative=combat.initiative,
        proficiency=combat.proficiency,
        armor=armor_name(translator, combat.armor_id),
        main_attack=main_attack_text(translator, character.class_id),
        starting_equipment=starting_equipment_text(translator, character),
        spells=spells_text(translator, character),
    )


def build_encounter_view(
    translator: Translator, encounter: Encounter
) -> EncounterView:
    """Turn an :class:`Encounter` into display text in one language."""
    stage = encounter.stage.value
    return EncounterView(
        stage=stage,
        label=translator.t(f"labels.{stage}_battle"),
        location=translator.t(f"encounters.locations.{encounter.location_id}"),
        enemies=tuple(
            EnemyView(
                name=translator.t(f"encounters.enemies.{enemy_id}.name"),
                type=translator.t(f"encounters.enemies.{enemy_id}.type"),
                armour=translator.t(f"encounters.enemies.{enemy_id}.armour"),
                goodies=translator.t(f"encounters.enemies.{enemy_id}.goodies"),
            )
            for enemy_id in encounter.enemy_ids
        ),
        unlock=(
            translator.t(f"encounters.unlocks.{encounter.unlock_id}")
            if encounter.unlock_id
            else None
        ),
    )


def build_universe_view(
    translator: Translator, universe: Universe
) -> UniverseView:
    """Turn a :class:`Universe` into display text in one language."""
    return UniverseView(
        universe_id=universe.universe_id,
        theme=translator.name("themes", universe.theme_id),
        factions=tuple(faction_name(translator, f) for f in universe.factions),
        settlements=tuple(
            translator.name("settlements", s) for s in universe.settlement_ids
        ),
        conflict=story_text(translator, universe.theme_id, universe.story),
        encounters=tuple(
            build_encounter_view(translator, e)
            for e in universe.encounters.stages
        ),
        party=tuple(
            build_character_view(translator, c) for c in universe.party
        ),
    )
