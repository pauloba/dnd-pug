"""Tests for the functions that turn character IDs into display text."""

import random

import pytest

from dnd_worldgen.generators.combat import build_combat_profile
from dnd_worldgen.generators.stats import generate_abilities
from dnd_worldgen.i18n import (
    Translator,
    armor_name,
    hook_text,
    main_attack_text,
    spells_text,
    starting_equipment_text,
)
from dnd_worldgen.models import Character, Faction, Language
from dnd_worldgen.rules.characters import (
    ALIGNMENT_IDS,
    BACKGROUND_IDS,
    CLASS_IDS,
    HOOK_IDS,
    RACE_IDS,
    SUBCLASS_IDS_BY_CLASS,
)
from dnd_worldgen.rules.classes import CLASSES
from dnd_worldgen.rules.themes import SETTLEMENT_IDS_BY_THEME, THEME_IDS

IRON_CRIMSON_GUILD = Faction("guild", "iron", "crimson")
SETTLEMENT_ID = SETTLEMENT_IDS_BY_THEME[THEME_IDS[0]][0]
EN = Translator.load(Language.EN)
ES = Translator.load(Language.ES)


def make_character(
    *,
    class_id: str = "fighter",
    subclass_id: str | None = None,
    race_id: str = "elf",
    background_id: str = "sage",
    hook_id: str = "hook_1",
) -> Character:
    abilities = generate_abilities(random.Random(0))
    return Character(
        name="Test",
        race_id=race_id,
        class_id=class_id,
        subclass_id=subclass_id or SUBCLASS_IDS_BY_CLASS[class_id][0],
        background_id=background_id,
        alignment_id=ALIGNMENT_IDS[0],
        level=1,
        faction=IRON_CRIMSON_GUILD,
        settlement_id=SETTLEMENT_ID,
        hook_id=hook_id,
        abilities=abilities,
        combat=build_combat_profile(class_id, abilities),
    )


# Expected strings are copied from the original script's output.


def test_armor_names() -> None:
    assert armor_name(EN, "chain_mail") == "Chain Mail"
    assert armor_name(ES, "chain_mail") == "Cota de malla"
    assert armor_name(EN, "robes") == "No Armor (Robes)"


def test_main_attack() -> None:
    assert (
        main_attack_text(EN, "fighter")
        == "Longsword (+5 to hit, 1d8+3 slashing)"
    )
    assert main_attack_text(ES, "fighter") == (
        "Espada larga (+5 para impactar, 1d8+3 cortante)"
    )


def test_starting_equipment_in_english() -> None:
    assert starting_equipment_text(EN, make_character()) == (
        "[Fighter Gear] Backpack, bedroll, mess kit, tinderbox, 10 torches, "
        "10 days of rations, waterskin. [Sage] Ink bottle, quill, small "
        "knife, letter from a dead colleague, common clothes, pouch with "
        "10 gp."
    )


def test_starting_equipment_in_spanish() -> None:
    assert starting_equipment_text(ES, make_character()) == (
        "[Equipo de Guerrero] Mochila, saco de dormir, kit de cocina, yesca y "
        "pedernal, 10 antorchas, 10 días de raciones, cantimplora. [Sabio] "
        "Frasco de tinta, pluma, cuchillo pequeño, carta de un colega "
        "difunto, ropa común, bolsa con 10 GP."
    )


def test_spells_mention_the_subclass() -> None:
    knight = make_character(subclass_id="eldritch_knight")
    assert spells_text(EN, knight) == (
        "Martial Superiority & Second Wind (Eldritch Knight). No innate "
        "spellcasting unless Eldritch Knight (Cantrips: Blade Ward, "
        "Fire Bolt)."
    )
    assert spells_text(ES, knight) == (
        "Superioridad marcial y Segundo aliento (Caballero Arcano). Sin "
        "conjuros nativos salvo Caballero Arcano (Trucos: Salvaguarda, "
        "Descarga de fuego)."
    )


@pytest.mark.parametrize("translator", [EN, ES])
def test_ranger_spells_mention_subclass_and_race(
    translator: Translator,
) -> None:
    ranger = make_character(class_id="ranger", race_id="half_orc")
    text = spells_text(translator, ranger)
    assert translator.name("subclasses", ranger.subclass_id) in text
    assert translator.name("races", "half_orc") in text


def test_hook_with_faction_and_settlement() -> None:
    text = hook_text(EN, make_character(hook_id="hook_1"))
    assert "The Iron Crimson Guild" in text
    assert EN.name("settlements", SETTLEMENT_ID) in text


def test_hook_that_only_uses_the_faction() -> None:
    assert hook_text(EN, make_character(hook_id="hook_3")) == (
        "An exiled scholar possessing forbidden knowledge coveted by "
        "The Iron Crimson Guild."
    )
    assert "Gremio de Hierro Carmesí" in hook_text(
        ES, make_character(hook_id="hook_3")
    )


# Nothing may ever leak an unfilled placeholder or raise, for any
# combination.


@pytest.mark.parametrize("language", list(Language))
def test_no_combination_leaves_a_placeholder_or_raises(
    language: Language,
) -> None:
    translator = Translator.load(language)
    for class_id in CLASS_IDS:
        texts = [
            main_attack_text(translator, class_id),
            armor_name(translator, CLASSES[class_id].armor_id),
        ]
        for subclass_id in SUBCLASS_IDS_BY_CLASS[class_id]:
            for race_id in RACE_IDS:
                for background_id in BACKGROUND_IDS:
                    character = make_character(
                        class_id=class_id,
                        subclass_id=subclass_id,
                        race_id=race_id,
                        background_id=background_id,
                    )
                    texts.append(spells_text(translator, character))
                    texts.append(
                        starting_equipment_text(translator, character)
                    )
        assert not any("{" in text or "}" in text for text in texts), class_id
    for hook_id in HOOK_IDS:
        text = hook_text(translator, make_character(hook_id=hook_id))
        assert "{" not in text and "}" not in text, hook_id
