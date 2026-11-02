"""Numeric combat statistics from class rules and ability scores.

Character level does not change any of these numbers: the original
generator never scaled hit points, armor class or the proficiency bonus
with level.
"""

from collections.abc import Mapping

from dnd_worldgen.models import AbilityScore, CombatProfile
from dnd_worldgen.rules.classes import CLASSES, PROFICIENCY_BONUS, ClassRules


def get_class_rules(class_id: str) -> ClassRules:
    """Return the rules of a class, failing loudly for an unknown ID."""
    try:
        return CLASSES[class_id]
    except KeyError:
        known = ", ".join(CLASSES)
        raise ValueError(
            f"Unknown class ID {class_id!r}. Known classes: {known}"
        ) from None


def compute_hit_points(rules: ClassRules, constitution_modifier: int) -> int:
    """Hit die plus the CON modifier, but never less than 1."""
    return max(1, rules.hit_die + constitution_modifier)


def compute_armor_class(rules: ClassRules, dexterity_modifier: int) -> int:
    """Return base armor class plus the DEX modifier for light armor.

    The modifier may be negative.
    """
    bonus = dexterity_modifier if rules.adds_dexterity else 0
    return rules.base_armor_class + bonus


def compute_initiative(dexterity_modifier: int) -> int:
    """Return the initiative, which equals the DEX modifier."""
    return dexterity_modifier


def build_combat_profile(
    class_id: str, abilities: Mapping[str, AbilityScore]
) -> CombatProfile:
    """Combine class rules and ability modifiers into a profile.

    Returns a :class:`CombatProfile`.
    """
    rules = get_class_rules(class_id)
    constitution = abilities["CON"].modifier
    dexterity = abilities["DEX"].modifier
    return CombatProfile(
        hp=compute_hit_points(rules, constitution),
        armor_class=compute_armor_class(rules, dexterity),
        initiative=compute_initiative(dexterity),
        proficiency=PROFICIENCY_BONUS,
        armor_id=rules.armor_id,
    )
