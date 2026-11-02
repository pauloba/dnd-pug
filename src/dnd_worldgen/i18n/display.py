"""Turn model IDs into display text for one language."""

from dnd_worldgen.i18n.translator import Translator
from dnd_worldgen.models import Character, Faction, Story


def faction_name(translator: Translator, faction: Faction) -> str:
    """Build a faction's display name in the translator's language.

    The pattern comes from ``factions.name_pattern`` because word order
    differs: English puts the type last ("The Iron Crimson Guild"),
    Spanish first ("Gremio Hierro Carmesi").
    """
    return translator.t(
        "factions.name_pattern",
        type=translator.t(f"factions.types.{faction.type_id}"),
        first_adjective=translator.t(
            f"factions.first_adjectives.{faction.first_adjective_id}"
        ),
        second_adjective=translator.t(
            f"factions.second_adjectives.{faction.second_adjective_id}"
        ),
    )


def hook_text(translator: Translator, character: Character) -> str:
    """Return the character's story hook, fully filled in.

    Faction and settlement names are inserted.
    """
    return translator.t(
        f"hooks.{character.hook_id}",
        faction=faction_name(translator, character.faction),
        settlement=translator.name("settlements", character.settlement_id),
    )


def armor_name(translator: Translator, armor_id: str) -> str:
    """Display name of an armor, e.g. ``chain_mail`` -> "Chain Mail"."""
    return translator.t(f"combat.armor.{armor_id}")


def main_attack_text(translator: Translator, class_id: str) -> str:
    """Return the class's signature attacks.

    Includes to-hit bonuses and damage dice.
    """
    return translator.t(f"combat.main_attacks.{class_id}")


def starting_equipment_text(
    translator: Translator, character: Character
) -> str:
    """Return class gear plus the background's starting kit.

    Both are joined into one paragraph.
    """
    return translator.t(
        "combat.starting_equipment",
        class_name=translator.name("classes", character.class_id),
        background_name=translator.name(
            "backgrounds", character.background_id
        ),
        background_equipment=translator.t(
            f"combat.background_equipment.{character.background_id}"
        ),
    )


def spells_text(translator: Translator, character: Character) -> str:
    """Return the class's magic and features as text.

    Mentions the subclass, and the race for some classes.
    """
    return translator.t(
        f"combat.spells.{character.class_id}",
        subclass=translator.name("subclasses", character.subclass_id),
        race=translator.name("races", character.race_id),
    )


def story_text(translator: Translator, theme_id: str, story: Story) -> str:
    """Return the campaign story as one text.

    Its paragraphs are filled in and joined.
    """
    paragraphs = translator.strings(f"stories.{theme_id}.{story.template_id}")
    params = {
        "theme_name": translator.name("themes", theme_id),
        "faction_a": faction_name(translator, story.faction_a),
        "faction_b": faction_name(translator, story.faction_b),
        "primary_settlement": translator.name(
            "settlements", story.primary_settlement_id
        ),
        "secondary_settlement": translator.name(
            "settlements", story.secondary_settlement_id
        ),
    }
    return " ".join(paragraph.format(**params) for paragraph in paragraphs)
