"""Tests for the view models, the templates and the PDF renderer."""

import dataclasses
import random
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

from dnd_worldgen.generators.universe import generate_universe
from dnd_worldgen.i18n import Translator
from dnd_worldgen.models import (
    Character,
    GenerationOptions,
    Language,
    Universe,
)
from dnd_worldgen.rendering import PdfBackendError, PdfRenderer, html_to_pdf
from dnd_worldgen.rendering.renderer import read_css
from dnd_worldgen.rendering.views import (
    SUBCLASS_FIELD_MIN_LEVEL,
    build_character_view,
    build_universe_view,
)
from dnd_worldgen.rules.themes import THEME_IDS

EN = Translator.load(Language.EN)
ES = Translator.load(Language.ES)


def make_universe(
    language: Language = Language.EN,
    theme_id: str = "steampunk",
    level: int = 1,
    players: int = 4,
    seed: int = 42,
) -> Universe:
    translator = Translator.load(language)
    options = GenerationOptions(
        theme_id=theme_id,
        language=language,
        num_players=players,
        character_level=level,
    )
    return generate_universe(options, random.Random(seed), translator)


class TagCounter(HTMLParser):
    """Counts opening and closing tags so unbalanced markup is
    noticed.
    """

    def __init__(self) -> None:
        super().__init__()
        self.opened: dict[str, int] = {}
        self.closed: dict[str, int] = {}

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.opened[tag] = self.opened.get(tag, 0) + 1

    def handle_endtag(self, tag: str) -> None:
        self.closed[tag] = self.closed.get(tag, 0) + 1


def assert_balanced(html: str) -> None:
    counter = TagCounter()
    counter.feed(html)
    void = {"meta"}  # tags that are never closed
    for tag, opened in counter.opened.items():
        if tag not in void:
            assert (
                counter.closed.get(tag, 0) == opened
            ), f"<{tag}> is unbalanced"


# --------------------------------------------------------------- view
# models


def test_character_view_matches_the_original_output() -> None:
    """Golden values read from the original's output (seed 42, first
    character).
    """
    view = build_character_view(EN, make_universe().party[0])
    assert view.name == "Gideon Sterling"
    assert (view.race, view.class_name, view.subclass) == (
        "Halfling",
        "Warlock",
        "The Archfey",
    )
    assert (view.background, view.alignment) == ("Acolyte", "Chaotic Evil")
    assert view.faction == "The Golden Solar Cult"
    assert [
        (s.attribute, s.label, s.score, s.modifier) for s in view.stats
    ] == [
        ("STR", "Strength", 12, 1),
        ("DEX", "Dexterity", 12, 1),
        ("CON", "Constitution", 8, -1),
        ("INT", "Intelligence", 8, -1),
        ("WIS", "Wisdom", 11, 0),
        ("CHA", "Charisma", 13, 1),
    ]
    assert (view.hit_points, view.armor_class) == (7, 12)
    assert (view.initiative, view.proficiency) == (1, 2)
    assert view.armor == "Leather Armor"


def test_stat_views_list_skills_per_ability() -> None:
    stats = {
        s.attribute: s
        for s in build_character_view(EN, make_universe().party[0]).stats
    }
    assert stats["STR"].skills == ("Athletics",)
    assert stats["CON"].skills == ()
    assert len(stats["DEX"].skills) == 3


@pytest.mark.parametrize(
    ("level", "shown"),
    [
        (1, False),
        (SUBCLASS_FIELD_MIN_LEVEL - 1, False),
        (SUBCLASS_FIELD_MIN_LEVEL, True),
        (20, True),
    ],
)
def test_subclass_field_appears_from_level_three(
    level: int, shown: bool
) -> None:
    character = make_universe(level=level).party[0]
    assert build_character_view(EN, character).shows_subclass_field is shown


def test_universe_view_has_three_encounter_stages_with_a_boss_unlock() -> None:
    view = build_universe_view(EN, make_universe())
    assert [e.stage for e in view.encounters] == ["low", "mid", "boss"]
    assert [e.unlock is not None for e in view.encounters] == [
        False,
        False,
        True,
    ]
    assert all(e.enemies for e in view.encounters)
    assert view.encounters[0].label == EN.t("labels.low_battle")


def test_universe_view_matches_the_original_output() -> None:
    """Golden values read from the original's output (seed 42, 4
    players).
    """
    view = build_universe_view(EN, make_universe(players=4))
    assert view.universe_id == "UNI-2876"
    assert view.theme == "High Fantasy Steampunk"
    assert view.factions == (
        "The Iron Crimson Eco-Engineers Alliance",
        "The Shadowed Silent Eco-Engineers Alliance",
        "The Golden Solar Cult",
    )
    assert view.settlements == ("Cogford", "Steam-Gallow", "Aether-Spire")
    assert len(view.party) == 4


def test_universe_view_party_follows_the_party_size() -> None:
    universe = make_universe(players=3)
    view = build_universe_view(EN, universe)
    assert len(view.party) == 3
    assert view.universe_id == universe.universe_id


# -----------------------------------------------------------------
# templates


def test_character_sheet_contents() -> None:
    universe = make_universe()
    character = universe.party[0]
    html = PdfRenderer(EN).render_character_html(character)
    assert "<title>D&amp;D CHARACTER SHEET - Gideon Sterling</title>" in html
    assert html.count('class="stat-box"') == 6
    assert html.count('class="combat-square"') == 4
    assert "Strength (STR)" in html
    assert (
        html.count("skill-list") == 5 + 1
    )  # five boxes list skills (+1 in the CSS)
    assert_balanced(html)


def test_modifiers_are_shown_with_a_sign() -> None:
    html = PdfRenderer(EN).render_character_html(make_universe().party[0])
    mods = re.findall(r'<div class="stat-mod">([^<]*)</div>', html)
    assert len(mods) == 6
    assert all(re.fullmatch(r"[+-]\d+", mod) for mod in mods)
    initiative = re.search(
        r"Initiative</div>\s*<div class=\"combat-square-value\">([^<]*)<", html
    )
    assert initiative and re.fullmatch(r"[+-]\d+", initiative.group(1))


def test_a_zero_modifier_is_shown_as_plus_zero() -> None:
    """The original sheet showed Wisdom 11 as "+0"."""
    html = PdfRenderer(EN).render_character_html(make_universe().party[0])
    assert re.findall(r'stat-mod">([^<]*)<', html) == [
        "+1",
        "+1",
        "-1",
        "-1",
        "+0",
        "+1",
    ]


def test_subclass_field_is_only_in_the_html_from_level_three() -> None:
    renderer = PdfRenderer(EN)
    low = renderer.render_character_html(make_universe(level=2).party[0])
    high = renderer.render_character_html(make_universe(level=3).party[0])
    assert "<label>Subclass</label>" not in low
    assert "<label>Subclass</label>" in high


def test_universe_document_contents() -> None:
    universe = make_universe(players=5)
    html = PdfRenderer(EN).render_universe_html(universe)
    assert html.count('class="encounter-card') == 3
    assert html.count('class="boss-unlock"') == 1
    assert html.count('class="boss-name"') == 1
    assert html.count('class="party-card"') == 5
    assert universe.universe_id in html
    assert_balanced(html)


def test_document_declares_its_language_and_embeds_the_css() -> None:
    en_html = PdfRenderer(EN).render_universe_html(make_universe())
    es_html = PdfRenderer(ES).render_universe_html(make_universe(Language.ES))
    assert '<html lang="en">' in en_html
    assert '<html lang="es">' in es_html
    assert "--accent" in en_html and ".encounter-card" in en_html


def test_no_template_syntax_leaks_into_the_output() -> None:
    renderer = PdfRenderer(EN)
    universe = make_universe(level=3)
    documents = [renderer.render_universe_html(universe)]
    documents += [renderer.render_character_html(c) for c in universe.party]
    for html in documents:
        body = html[html.index("<body>") :]
        assert "{{" not in body and "{%" not in body and "{#" not in body


def test_spanish_documents_use_spanish_labels_and_a_real_title() -> None:
    universe = make_universe(Language.ES)
    renderer = PdfRenderer(ES)
    character_html = renderer.render_character_html(universe.party[0])
    name = universe.party[0].name
    title = f"<title>HOJA DE PERSONAJE DE D&amp;D - {name}</title>"
    assert title in character_html
    assert "<label>Raza</label>" in character_html
    assert "Manual del Universo D&amp;D" in renderer.render_universe_html(
        universe
    )


def test_generated_text_is_escaped() -> None:
    universe = make_universe()
    hostile: Character = dataclasses.replace(
        universe.party[0], name='<script>alert("x")</script> & Co'
    )
    html = PdfRenderer(EN).render_character_html(hostile)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html and "&amp; Co" in html


@pytest.mark.parametrize("language", list(Language))
@pytest.mark.parametrize("theme_id", THEME_IDS)
def test_every_theme_renders_in_every_language(
    theme_id: str, language: Language
) -> None:
    universe = make_universe(language, theme_id, level=3, players=6)
    renderer = PdfRenderer(Translator.load(language))
    assert_balanced(renderer.render_universe_html(universe))
    for character in universe.party:
        assert_balanced(renderer.render_character_html(character))


def test_css_files_are_read_in_order() -> None:
    combined = read_css("base.css", "universe.css")
    assert combined.index(":root") < combined.index(".encounter-card")
    assert read_css("base.css", "universe.css") is combined  # cached


# ---------------------------------------------------------------------
# PDF


def test_pdf_files_are_written(tmp_path: Path) -> None:
    try:
        import weasyprint  # noqa: F401
    except (ImportError, OSError):
        pytest.skip("WeasyPrint's system libraries are not available here")
    universe = make_universe()
    renderer = PdfRenderer(EN)
    renderer.write_universe_pdf(universe, tmp_path / "game.pdf")
    renderer.write_character_pdf(
        universe.party[0], tmp_path / "character1.pdf"
    )
    for name in ("game.pdf", "character1.pdf"):
        assert (tmp_path / name).read_bytes().startswith(b"%PDF")


def test_html_to_pdf_writes_a_pdf(tmp_path: Path) -> None:
    try:
        import weasyprint  # noqa: F401
    except (ImportError, OSError):
        pytest.skip("WeasyPrint's system libraries are not available here")
    target = tmp_path / "one.pdf"
    html_to_pdf("<html><body><p>Hello</p></body></html>", target)
    assert target.read_bytes().startswith(b"%PDF")


def test_a_missing_weasyprint_gives_a_helpful_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setitem(
        sys.modules, "weasyprint", None
    )  # makes the import fail
    with pytest.raises(PdfBackendError, match="WeasyPrint"):
        html_to_pdf("<p>x</p>", tmp_path / "x.pdf")
    assert not (tmp_path / "x.pdf").exists()
