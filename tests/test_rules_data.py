"""Integrity tests: the rules modules and the locale files must agree.

Every ID the rules mention needs text in every language, and the locale
files must not contain dead entries that no rule refers to.
"""

import json
import re
from pathlib import Path
from typing import Any

import pytest

import dnd_worldgen
from dnd_worldgen.config import STAT_NAMES
from dnd_worldgen.models import EncounterStage
from dnd_worldgen.rules.attributes import SKILL_IDS_BY_ATTRIBUTE
from dnd_worldgen.rules.characters import (
    ALIGNMENT_IDS,
    BACKGROUND_IDS,
    CLASS_IDS,
    HOOK_IDS,
    RACE_IDS,
    SUBCLASS_IDS_BY_CLASS,
)
from dnd_worldgen.rules.classes import CLASSES
from dnd_worldgen.rules.encounters import ENCOUNTERS_BY_THEME
from dnd_worldgen.rules.factions import (
    FACTION_TYPE_IDS,
    FIRST_ADJECTIVE_IDS,
    SECOND_ADJECTIVE_IDS,
)
from dnd_worldgen.rules.stories import STORY_IDS_BY_THEME
from dnd_worldgen.rules.themes import (
    DEFAULT_THEME_ID,
    SETTLEMENT_IDS_BY_THEME,
    THEME_IDS,
    require_theme,
)

LOCALES = Path(dnd_worldgen.__file__).parent / "i18n" / "locales"
LANGUAGES = ("en", "es")
ENEMY_FIELDS = {"name", "type", "armour", "goodies"}
HOOK_PLACEHOLDERS = {"faction", "settlement"}
SPELL_PLACEHOLDERS = {"subclass", "race"}
STORY_PLACEHOLDERS = {
    "theme_name",
    "faction_a",
    "faction_b",
    "primary_settlement",
    "secondary_settlement",
}
PARAGRAPHS_PER_STORY = 3
EQUIPMENT_PLACEHOLDERS = {
    "class_name",
    "background_name",
    "background_equipment",
}
ARMOR_IDS = tuple(dict.fromkeys(rules.armor_id for rules in CLASSES.values()))

SUBCLASS_IDS = tuple(s for c in CLASS_IDS for s in SUBCLASS_IDS_BY_CLASS[c])
SKILL_IDS = tuple(s for ids in SKILL_IDS_BY_ATTRIBUTE.values() for s in ids)
SETTLEMENT_IDS = tuple(
    s for t in THEME_IDS for s in SETTLEMENT_IDS_BY_THEME[t]
)
ENCOUNTERS = [e for t in THEME_IDS for e in ENCOUNTERS_BY_THEME[t].stages]


def load(lang: str, name: str) -> Any:
    path = LOCALES / lang / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


# ------------------------------------------------------------ rules
# alone


@pytest.mark.parametrize(
    "ids",
    [
        THEME_IDS,
        FACTION_TYPE_IDS,
        FIRST_ADJECTIVE_IDS,
        SECOND_ADJECTIVE_IDS,
        ALIGNMENT_IDS,
        RACE_IDS,
        CLASS_IDS,
        BACKGROUND_IDS,
        HOOK_IDS,
        SUBCLASS_IDS,
        SKILL_IDS,
        SETTLEMENT_IDS,
        tuple(loc for e in ENCOUNTERS for loc in [e.location_id]),
        tuple(enemy for e in ENCOUNTERS for enemy in e.enemy_ids),
    ],
)
def test_ids_are_unique(ids: tuple[str, ...]) -> None:
    assert len(ids) == len(set(ids))
    assert all(re.fullmatch(r"[a-z0-9_]+", i) for i in ids)


def test_default_theme_is_the_first_menu_entry() -> None:
    assert DEFAULT_THEME_ID == THEME_IDS[0]


def test_skills_are_defined_for_every_stat_in_order() -> None:
    assert tuple(SKILL_IDS_BY_ATTRIBUTE) == STAT_NAMES


def test_every_class_has_subclasses() -> None:
    assert tuple(SUBCLASS_IDS_BY_CLASS) == CLASS_IDS
    assert all(SUBCLASS_IDS_BY_CLASS[c] for c in CLASS_IDS)


def test_every_theme_has_settlements_and_encounters() -> None:
    assert set(SETTLEMENT_IDS_BY_THEME) == set(THEME_IDS)
    assert set(ENCOUNTERS_BY_THEME) == set(THEME_IDS)
    assert all(len(SETTLEMENT_IDS_BY_THEME[t]) >= 2 for t in THEME_IDS)


def test_encounter_stages_are_in_order_and_only_boss_unlocks() -> None:
    for theme_id in THEME_IDS:
        stages = ENCOUNTERS_BY_THEME[theme_id].stages
        assert [e.stage for e in stages] == list(EncounterStage)
        assert all(e.enemy_ids for e in stages)
        assert [e.unlock_id is not None for e in stages] == [
            False,
            False,
            True,
        ]


# -------------------------------------------------- rules against
# locales


def assert_same_ids(
    actual: Any, expected: tuple[str, ...], where: str
) -> None:
    """Locale file must define exactly the IDs the rules mention."""
    assert set(actual) == set(expected), (
        f"{where}: missing {set(expected) - set(actual)}, "
        f"unused {set(actual) - set(expected)}"
    )


@pytest.mark.parametrize("lang", LANGUAGES)
def test_simple_name_files_cover_all_ids(lang: str) -> None:
    assert_same_ids(load(lang, "themes"), THEME_IDS, "themes")
    assert_same_ids(load(lang, "skills"), SKILL_IDS, "skills")
    assert_same_ids(load(lang, "settlements"), SETTLEMENT_IDS, "settlements")
    assert_same_ids(load(lang, "hooks"), HOOK_IDS, "hooks")
    assert_same_ids(load(lang, "names"), THEME_IDS, "names")
    for texts in (
        load(lang, "themes"),
        load(lang, "skills"),
        load(lang, "settlements"),
        load(lang, "hooks"),
    ):
        assert all(isinstance(t, str) and t.strip() for t in texts.values())


@pytest.mark.parametrize("lang", LANGUAGES)
@pytest.mark.parametrize(
    ("file", "ids"),
    [
        ("alignments", ALIGNMENT_IDS),
        ("races", RACE_IDS),
        ("classes", CLASS_IDS),
        ("backgrounds", BACKGROUND_IDS),
        ("subclasses", SUBCLASS_IDS),
    ],
)
def test_described_files_have_name_and_description(
    lang: str, file: str, ids: tuple[str, ...]
) -> None:
    data = load(lang, file)
    assert_same_ids(data, ids, file)
    for entry in data.values():
        assert set(entry) == {"name", "description"}
        assert entry["name"].strip() and entry["description"].strip()


@pytest.mark.parametrize("lang", LANGUAGES)
def test_faction_pools_cover_all_ids(lang: str) -> None:
    factions = load(lang, "factions")
    assert_same_ids(factions["types"], FACTION_TYPE_IDS, "faction types")
    assert_same_ids(
        factions["first_adjectives"], FIRST_ADJECTIVE_IDS, "adjectives 1"
    )
    assert_same_ids(
        factions["second_adjectives"], SECOND_ADJECTIVE_IDS, "adjectives 2"
    )


@pytest.mark.parametrize("lang", LANGUAGES)
def test_encounter_text_covers_all_referenced_ids(lang: str) -> None:
    data = load(lang, "encounters")
    assert_same_ids(
        data["locations"],
        tuple(e.location_id for e in ENCOUNTERS),
        "locations",
    )
    assert_same_ids(
        data["enemies"],
        tuple(i for e in ENCOUNTERS for i in e.enemy_ids),
        "enemies",
    )
    assert_same_ids(
        data["unlocks"],
        tuple(e.unlock_id for e in ENCOUNTERS if e.unlock_id),
        "unlocks",
    )
    for enemy in data["enemies"].values():
        assert set(enemy) == ENEMY_FIELDS
        assert all(value.strip() for value in enemy.values())


@pytest.mark.parametrize("lang", LANGUAGES)
def test_hooks_only_use_known_placeholders(lang: str) -> None:
    for hook_id, text in load(lang, "hooks").items():
        used = set(re.findall(r"\{(\w+)\}", text))
        assert (
            used <= HOOK_PLACEHOLDERS
        ), f"{hook_id}: unknown placeholder in {used}"
        assert "faction" in used


def test_languages_agree_on_shape() -> None:
    en_hooks, es_hooks = load("en", "hooks"), load("es", "hooks")
    for hook_id in HOOK_IDS:
        assert set(re.findall(r"\{(\w+)\}", en_hooks[hook_id])) == set(
            re.findall(r"\{(\w+)\}", es_hooks[hook_id])
        )
    en_names, es_names = load("en", "names"), load("es", "names")
    assert all(len(en_names[t]) == len(es_names[t]) >= 1 for t in THEME_IDS)
    assert set(load("en", "labels")) == set(load("es", "labels"))


@pytest.mark.parametrize("lang", LANGUAGES)
def test_combat_text_covers_every_class_background_and_armor(
    lang: str,
) -> None:
    data = load(lang, "combat")
    assert_same_ids(data["main_attacks"], CLASS_IDS, "main_attacks")
    assert_same_ids(data["spells"], CLASS_IDS, "spells")
    assert_same_ids(
        data["background_equipment"], BACKGROUND_IDS, "background_equipment"
    )
    assert_same_ids(data["armor"], ARMOR_IDS, "armor")
    for section in ("main_attacks", "spells", "background_equipment", "armor"):
        assert all(text.strip() for text in data[section].values()), section


@pytest.mark.parametrize("lang", LANGUAGES)
def test_combat_templates_use_only_known_placeholders(lang: str) -> None:
    data = load(lang, "combat")
    used = set(re.findall(r"\{(\w+)\}", data["starting_equipment"]))
    assert used == EQUIPMENT_PLACEHOLDERS
    for class_id, text in data["spells"].items():
        used = set(re.findall(r"\{(\w+)\}", text))
        assert "subclass" in used and used <= SPELL_PLACEHOLDERS, class_id


# ------------------------------------------------------------ stories,
# party


def test_every_theme_has_stories() -> None:
    assert set(STORY_IDS_BY_THEME) == set(THEME_IDS)
    assert all(len(ids) >= 1 for ids in STORY_IDS_BY_THEME.values())


@pytest.mark.parametrize("lang", LANGUAGES)
def test_story_text_covers_every_story(lang: str) -> None:
    stories = load(lang, "stories")
    assert_same_ids(stories, THEME_IDS, "stories")
    for theme_id in THEME_IDS:
        assert_same_ids(
            stories[theme_id], STORY_IDS_BY_THEME[theme_id], theme_id
        )
        for story_id, paragraphs in stories[theme_id].items():
            where = f"{theme_id}/{story_id}"
            assert len(paragraphs) == PARAGRAPHS_PER_STORY, where
            assert all(p.strip() for p in paragraphs), where
            used = {
                name
                for p in paragraphs
                for name in re.findall(r"\{(\w+)\}", p)
            }
            assert used <= STORY_PLACEHOLDERS, f"{where}: unknown {used}"


def test_languages_use_the_same_placeholders_in_each_story() -> None:
    """Paragraphs are joined, so only the placeholders overall must
    agree.
    """
    en, es = load("en", "stories"), load("es", "stories")
    for theme_id in THEME_IDS:
        for story_id in STORY_IDS_BY_THEME[theme_id]:
            used = [
                {
                    n
                    for p in stories[theme_id][story_id]
                    for n in re.findall(r"\{(\w+)\}", p)
                }
                for stories in (en, es)
            ]
            assert used[0] == used[1], f"{theme_id}/{story_id}"


@pytest.mark.parametrize("lang", LANGUAGES)
def test_fallback_party_name_takes_a_number(lang: str) -> None:
    party = load(lang, "party")
    assert set(party) == {"fallback_name"}
    assert re.findall(r"\{(\w+)\}", party["fallback_name"]) == ["number"]


def test_require_theme() -> None:
    assert require_theme("steampunk") == "steampunk"
    with pytest.raises(ValueError, match="Unknown theme ID 'x'.*steampunk"):
        require_theme("x")
