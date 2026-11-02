"""Tests for faction, story and encounter generation and the story
text.
"""

import random
import re

import pytest

from dnd_worldgen.generators.encounters import get_encounters
from dnd_worldgen.generators.factions import (
    generate_faction,
    generate_factions,
)
from dnd_worldgen.generators.story import generate_story
from dnd_worldgen.i18n import Translator, faction_name, story_text
from dnd_worldgen.models import EncounterStage, Faction, Language, Story
from dnd_worldgen.rules.encounters import ENCOUNTERS_BY_THEME
from dnd_worldgen.rules.factions import (
    FACTION_TYPE_IDS,
    FIRST_ADJECTIVE_IDS,
    SECOND_ADJECTIVE_IDS,
)
from dnd_worldgen.rules.stories import STORY_IDS_BY_THEME
from dnd_worldgen.rules.themes import SETTLEMENT_IDS_BY_THEME, THEME_IDS

FACTIONS = (
    Faction("guild", "iron", "crimson"),
    Faction("cult", "golden", "silent"),
    Faction("empire", "shadowed", "solar"),
)
SETTLEMENTS = SETTLEMENT_IDS_BY_THEME["steampunk"][:3]


# ------------------------------------------------------------------
# factions


def test_faction_draws_type_then_first_then_second_adjective() -> None:
    rng = random.Random(5)
    expected = Faction(
        rng.choice(FACTION_TYPE_IDS),
        rng.choice(FIRST_ADJECTIVE_IDS),
        rng.choice(SECOND_ADJECTIVE_IDS),
    )
    assert generate_faction(random.Random(5)) == expected


@pytest.mark.parametrize("count", [1, 3, 5])
def test_generate_factions_count_and_valid_parts(count: int) -> None:
    factions = generate_factions(random.Random(1), count)
    assert len(factions) == count
    for faction in factions:
        assert faction.type_id in FACTION_TYPE_IDS
        assert faction.first_adjective_id in FIRST_ADJECTIVE_IDS
        assert faction.second_adjective_id in SECOND_ADJECTIVE_IDS


def test_default_is_three_factions() -> None:
    assert len(generate_factions(random.Random(1))) == 3


def test_factions_use_only_the_given_rng() -> None:
    random.seed(1)
    before = random.getstate()
    generate_factions(random.Random(9))
    assert random.getstate() == before


# ---------------------------------------------------------------------
# story


def test_story_uses_the_first_two_factions_and_settlements() -> None:
    story = generate_story(
        random.Random(1), "steampunk", FACTIONS, SETTLEMENTS
    )
    assert story.faction_a == FACTIONS[0]
    assert story.faction_b == FACTIONS[1]
    assert story.primary_settlement_id == SETTLEMENTS[0]
    assert story.secondary_settlement_id == SETTLEMENTS[1]


@pytest.mark.parametrize("theme_id", THEME_IDS)
def test_story_template_belongs_to_the_theme(theme_id: str) -> None:
    settlements = SETTLEMENT_IDS_BY_THEME[theme_id][:3]
    for seed in range(20):
        story = generate_story(
            random.Random(seed), theme_id, FACTIONS, settlements
        )
        assert story.template_id in STORY_IDS_BY_THEME[theme_id]


def test_story_makes_exactly_one_random_draw() -> None:
    rng = random.Random(3)
    generate_story(rng, "steampunk", FACTIONS, SETTLEMENTS)
    reference = random.Random(3)
    reference.choice(STORY_IDS_BY_THEME["steampunk"])
    assert rng.random() == reference.random()


def test_story_rejects_bad_input() -> None:
    rng = random.Random(1)
    with pytest.raises(ValueError, match="Unknown theme ID 'nope'"):
        generate_story(rng, "nope", FACTIONS, SETTLEMENTS)
    with pytest.raises(ValueError, match="two factions"):
        generate_story(rng, "steampunk", FACTIONS[:1], SETTLEMENTS)
    with pytest.raises(ValueError, match="two settlements"):
        generate_story(rng, "steampunk", FACTIONS, SETTLEMENTS[:1])


def test_story_text_matches_the_original_for_seed_42() -> None:
    """Golden: the original's universe for seed 42 (English,
    steampunk).
    """
    translator = Translator.load(Language.EN)
    story = Story(
        "story_4",
        Faction("eco_engineers_alliance", "iron", "crimson"),
        Faction("eco_engineers_alliance", "shadowed", "silent"),
        "cogford",
        "steam_gallow",
    )
    assert story_text(translator, "steampunk", story).startswith(
        "An astronomical discovery atop the Grand Spire of Cogford "
        "revealed an arcane quartz comet hurtling toward Steam-Gallow."
    )


@pytest.mark.parametrize("language", list(Language))
def test_every_story_renders_completely(language: Language) -> None:
    translator = Translator.load(language)
    for theme_id in THEME_IDS:
        settlements = SETTLEMENT_IDS_BY_THEME[theme_id]
        for story_id in STORY_IDS_BY_THEME[theme_id]:
            story = Story(
                story_id,
                FACTIONS[0],
                FACTIONS[1],
                settlements[0],
                settlements[1],
            )
            text = story_text(translator, theme_id, story)
            assert text.strip(), (theme_id, story_id)
            assert not re.search(r"[{}]", text), (theme_id, story_id)
            assert faction_name(translator, FACTIONS[0]) in text, (
                theme_id,
                story_id,
            )


def test_the_solarpunk_story_mentions_the_theme_name() -> None:
    translator = Translator.load(Language.EN)
    settlements = SETTLEMENT_IDS_BY_THEME["solarpunk"]
    story = Story(
        "story_1", FACTIONS[0], FACTIONS[1], settlements[0], settlements[1]
    )
    assert "Solarpunk Arcane Canopy" in story_text(
        translator, "solarpunk", story
    )


# ----------------------------------------------------------------
# encounters


@pytest.mark.parametrize("theme_id", THEME_IDS)
def test_get_encounters_returns_the_theme_dossier(theme_id: str) -> None:
    encounters = get_encounters(theme_id)
    assert encounters is ENCOUNTERS_BY_THEME[theme_id]
    assert [e.stage for e in encounters.stages] == list(EncounterStage)


def test_unknown_theme_has_no_encounters() -> None:
    with pytest.raises(ValueError, match="Unknown theme ID 'nope'.*steampunk"):
        get_encounters("nope")
