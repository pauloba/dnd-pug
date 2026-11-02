"""Class rules: hit die and armor. Names live in the locale files.

Originally extracted from the tables of the first, single-file
version of the generator (see the git history). It is now
hand-maintained: edit it directly.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

#: Proficiency bonus. The original generator used a fixed +2 at every
#: level.
PROFICIENCY_BONUS: Final = 2


@dataclass(frozen=True)
class ClassRules:
    """What a class contributes to hit points and armor class."""

    hit_die: int
    armor_id: str
    base_armor_class: int
    adds_dexterity: (
        bool  # light armor adds the DEX modifier, heavy armor does not
    )


CLASSES: Final[Mapping[str, ClassRules]] = {
    "fighter": ClassRules(
        hit_die=10,
        armor_id="chain_mail",
        base_armor_class=16,
        adds_dexterity=False,
    ),
    "wizard": ClassRules(
        hit_die=6, armor_id="robes", base_armor_class=10, adds_dexterity=True
    ),
    "rogue": ClassRules(
        hit_die=8,
        armor_id="leather_armor",
        base_armor_class=11,
        adds_dexterity=True,
    ),
    "cleric": ClassRules(
        hit_die=8,
        armor_id="scale_mail_and_shield",
        base_armor_class=16,
        adds_dexterity=False,
    ),
    "ranger": ClassRules(
        hit_die=10,
        armor_id="studded_leather_armor",
        base_armor_class=12,
        adds_dexterity=True,
    ),
    "paladin": ClassRules(
        hit_die=10,
        armor_id="chain_mail_and_shield",
        base_armor_class=18,
        adds_dexterity=False,
    ),
    "bard": ClassRules(
        hit_die=8,
        armor_id="leather_armor",
        base_armor_class=11,
        adds_dexterity=True,
    ),
    "druid": ClassRules(
        hit_die=8,
        armor_id="hide_armor_and_shield",
        base_armor_class=14,
        adds_dexterity=False,
    ),
    "warlock": ClassRules(
        hit_die=8,
        armor_id="leather_armor",
        base_armor_class=11,
        adds_dexterity=True,
    ),
}
