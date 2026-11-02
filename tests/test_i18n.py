"""Tests for the translator, locale parity between languages, and
faction names.
"""

import copy
import re
from collections.abc import Mapping
from typing import Any

import pytest

from dnd_worldgen.i18n import (
    TranslationError,
    Translator,
    faction_name,
    load_catalog,
)
from dnd_worldgen.models import Faction, Language

PLACEHOLDER = re.compile(r"\{(\w+)\}")

SMALL_CATALOG: dict[str, Any] = {
    "classes": {"fighter": {"name": "Fighter", "description": "Strong."}},
    "skills": {"stealth": "Stealth"},
    "hooks": {
        "hook_1": "Works for {faction} in {settlement}",
        "hook_2": "For {faction}",
    },
    "names": {"theme": ["Ada", "Bo"], "mixed": ["Ada", 3]},
}


@pytest.fixture
def small() -> Translator:
    return Translator(Language.EN, SMALL_CATALOG)


# --------------------------------------------------------- Translator
# basics


def test_t_returns_text(small: Translator) -> None:
    assert small.t("skills.stealth") == "Stealth"
    assert small.t("classes.fighter.name") == "Fighter"


def test_t_fills_parameters(small: Translator) -> None:
    text = small.t("hooks.hook_1", faction="Iron Guild", settlement="Cogford")
    assert text == "Works for Iron Guild in Cogford"


def test_t_ignores_extra_parameters(small: Translator) -> None:
    assert small.t("hooks.hook_2", faction="Iron Guild", settlement="x") == (
        "For Iron Guild"
    )


def test_t_without_parameters_returns_the_raw_template(
    small: Translator,
) -> None:
    assert small.t("hooks.hook_1") == "Works for {faction} in {settlement}"


def test_t_allows_a_parameter_called_key(small: Translator) -> None:
    assert small.t("skills.stealth", key="unused") == "Stealth"


def test_get_returns_raw_values(small: Translator) -> None:
    assert small.get("names.theme") == ["Ada", "Bo"]
    assert small.get("classes.fighter") == {
        "name": "Fighter",
        "description": "Strong.",
    }


def test_has(small: Translator) -> None:
    assert small.has("skills.stealth")
    assert small.has("classes")
    assert not small.has("skills.athletics")
    assert not small.has("nonsense.at.all")


def test_strings_returns_a_tuple(small: Translator) -> None:
    assert small.strings("names.theme") == ("Ada", "Bo")


def test_name_handles_both_layouts(small: Translator) -> None:
    assert small.name("skills", "stealth") == "Stealth"
    assert small.name("classes", "fighter") == "Fighter"


def test_description(small: Translator) -> None:
    assert small.description("classes", "fighter") == "Strong."


def test_language_property(small: Translator) -> None:
    assert small.language is Language.EN


# --------------------------------------------------------------- error
# cases


def test_missing_key_message_names_key_and_language() -> None:
    translator = Translator(Language.ES, SMALL_CATALOG)
    with pytest.raises(TranslationError) as info:
        translator.t("skills.athletics")
    message = str(info.value)
    assert "'skills.athletics'" in message
    assert "'es'" in message
    assert "'athletics' not found in 'skills'" in message


def test_missing_top_level_file_is_reported(small: Translator) -> None:
    with pytest.raises(TranslationError, match="not found in 'the catalog'"):
        small.t("clases.fighter.name")


def test_missing_key_suggests_close_matches(small: Translator) -> None:
    with pytest.raises(TranslationError, match="did you mean 'fighter'"):
        small.t("classes.figther.name")


def test_walking_into_text_is_reported(small: Translator) -> None:
    with pytest.raises(TranslationError, match="'skills.stealth' is a value"):
        small.t("skills.stealth.name")


@pytest.mark.parametrize(
    "key", ["", ".", "skills.", ".skills", "skills..stealth"]
)
def test_malformed_keys_raise_translation_error(
    small: Translator, key: str
) -> None:
    with pytest.raises(TranslationError):
        small.get(key)


def test_t_on_a_section_or_list_explains_what_to_use(
    small: Translator,
) -> None:
    with pytest.raises(TranslationError, match="not text"):
        small.t("classes.fighter")
    with pytest.raises(TranslationError, match="list, not text"):
        small.t("names.theme")


def test_missing_parameter_is_reported(small: Translator) -> None:
    with pytest.raises(TranslationError) as info:
        small.t("hooks.hook_1", faction="Iron Guild")
    assert "hooks.hook_1" in str(info.value)
    assert "settlement" in str(info.value)


def test_strings_rejects_non_lists(small: Translator) -> None:
    with pytest.raises(TranslationError, match="not a list of text"):
        small.strings("skills.stealth")
    with pytest.raises(TranslationError, match="not a list of text"):
        small.strings("names.mixed")


def test_translation_error_is_a_key_error_with_a_plain_message(
    small: Translator,
) -> None:
    with pytest.raises(KeyError) as info:
        small.t("nope")
    assert not str(info.value).startswith(('"', "'"))


# ------------------------------------------------------ packaged locale
# files


@pytest.mark.parametrize("language", list(Language))
def test_every_language_has_locale_files(language: Language) -> None:
    assert load_catalog(
        language
    ), f"no locale files found for {language.value}"


def test_catalog_is_loaded_once() -> None:
    assert load_catalog(Language.EN) is load_catalog(Language.EN)


def test_packaged_locales_resolve_real_keys() -> None:
    en, es = Translator.load(Language.EN), Translator.load(Language.ES)
    assert en.t("classes.fighter.name") == "Fighter"
    assert es.t("classes.fighter.name") == "Guerrero"
    assert en.name("races", "half_orc") != es.name("races", "half_orc")


# ------------------------------------------------- parity between
# languages


def flatten(catalog: Mapping[str, Any]) -> dict[str, Any]:
    """``{file: {a: {b: "x"}}}`` -> ``{"file.a.b": "x"}``. Lists are
    leaves.
    """
    flat: dict[str, Any] = {}

    def walk(node: Any, path: str) -> None:
        if isinstance(node, Mapping):
            for key, value in node.items():
                assert (
                    "." not in key
                ), f"key {key!r} under {path!r} contains a dot"
                walk(value, f"{path}.{key}" if path else key)
        else:
            flat[path] = node

    walk(catalog, "")
    return flat


def placeholder_union(texts: list[Any]) -> set[str]:
    return {
        name
        for text in texts
        if isinstance(text, str)
        for name in PLACEHOLDER.findall(text)
    }


def find_parity_problems(
    en: Mapping[str, Any], es: Mapping[str, Any]
) -> list[str]:
    """Describe every way two languages disagree. Empty list means
    parity.
    """
    problems: list[str] = []
    en_flat, es_flat = flatten(en), flatten(es)

    for key in sorted(set(en_flat) - set(es_flat)):
        problems.append(f"missing in es: {key}")
    for key in sorted(set(es_flat) - set(en_flat)):
        problems.append(f"missing in en: {key}")

    for key in sorted(set(en_flat) & set(es_flat)):
        for lang, flat in (("en", en_flat), ("es", es_flat)):
            value = flat[key]
            texts = value if isinstance(value, list) else [value]
            if (
                not all(isinstance(t, str) and t.strip() for t in texts)
                or not texts
            ):
                problems.append(f"empty or non-text value in {lang}: {key}")
        en_value, es_value = en_flat[key], es_flat[key]
        if isinstance(en_value, str) and isinstance(es_value, str):
            if set(PLACEHOLDER.findall(en_value)) != set(
                PLACEHOLDER.findall(es_value)
            ):
                problems.append(f"placeholders differ: {key}")
        elif isinstance(en_value, list) != isinstance(es_value, list):
            problems.append(f"text in one language, list in the other: {key}")
        elif isinstance(en_value, list) and isinstance(es_value, list):
            # Lists of paragraphs are joined, so compare the
            # placeholders overall.
            if placeholder_union(en_value) != placeholder_union(es_value):
                problems.append(f"placeholders differ: {key}")
    return problems


def test_languages_have_identical_keys_and_placeholders() -> None:
    problems = find_parity_problems(
        load_catalog(Language.EN), load_catalog(Language.ES)
    )
    assert problems == []


def test_every_language_has_the_same_locale_files() -> None:
    assert {
        tuple(sorted(load_catalog(language))) for language in Language
    } == {tuple(sorted(load_catalog(Language.EN)))}


@pytest.mark.parametrize("language", list(Language))
def test_every_key_is_reachable_through_the_translator(
    language: Language,
) -> None:
    translator = Translator.load(language)
    for key, value in flatten(load_catalog(language)).items():
        assert translator.get(key) == value, key
        if isinstance(value, str):
            assert translator.t(key) == value


# The checker above must itself notice problems, or the parity test is
# worthless.


@pytest.fixture
def pair() -> tuple[dict[str, Any], dict[str, Any]]:
    en = {"a": {"x": "Hi {name}", "y": ["p", "q"]}, "b": "Text"}
    return en, copy.deepcopy(en)


def test_parity_checker_accepts_matching_catalogs(
    pair: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    assert find_parity_problems(*pair) == []


def test_parity_checker_detects_a_missing_key(
    pair: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    en, es = pair
    del es["a"]["x"]
    assert find_parity_problems(en, es) == ["missing in es: a.x"]


def test_parity_checker_detects_an_extra_key(
    pair: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    en, es = pair
    es["c"] = "Extra"
    assert find_parity_problems(en, es) == ["missing in en: c"]


def test_parity_checker_detects_a_missing_file(
    pair: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    en, es = pair
    del es["b"]
    assert find_parity_problems(en, es) == ["missing in es: b"]


def test_parity_checker_detects_changed_placeholders(
    pair: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    en, es = pair
    es["a"]["x"] = "Hola {nombre}"
    assert find_parity_problems(en, es) == ["placeholders differ: a.x"]


def test_parity_checker_detects_empty_text(
    pair: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    en, es = pair
    es["b"] = "  "
    es["a"]["y"] = []
    assert find_parity_problems(en, es) == [
        "empty or non-text value in es: a.y",
        "empty or non-text value in es: b",
    ]


def test_parity_checker_detects_text_versus_list(
    pair: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    en, es = pair
    es["a"]["y"] = "p q"
    assert find_parity_problems(en, es) == [
        "text in one language, list in the other: a.y"
    ]


def test_parity_checker_compares_placeholders_across_a_list_of_paragraphs(
    pair: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    en, es = pair
    en["a"]["y"] = ["One {a}", "Two {b}"]
    es["a"]["y"] = ["Uno {b}", "Dos {a}"]  # spread differently: fine
    assert find_parity_problems(en, es) == []
    es["a"]["y"] = ["Uno {a}", "Dos"]  # {b} lost overall
    assert find_parity_problems(en, es) == ["placeholders differ: a.y"]


# ------------------------------------------------------------ faction
# names


IRON_CRIMSON_GUILD = Faction("guild", "iron", "crimson")


def test_faction_name_in_english_puts_the_type_last() -> None:
    translator = Translator.load(Language.EN)
    assert (
        faction_name(translator, IRON_CRIMSON_GUILD)
        == "The Iron Crimson Guild"
    )


def test_faction_name_in_spanish_puts_the_type_first() -> None:
    translator = Translator.load(Language.ES)
    assert (
        faction_name(translator, IRON_CRIMSON_GUILD)
        == "Gremio de Hierro Carmesí"
    )


def test_every_faction_combination_builds_a_name_in_every_language() -> None:
    from dnd_worldgen.rules.factions import (
        FACTION_TYPE_IDS,
        FIRST_ADJECTIVE_IDS,
        SECOND_ADJECTIVE_IDS,
    )

    for language in Language:
        translator = Translator.load(language)
        names = {
            faction_name(translator, Faction(t, a, b))
            for t in FACTION_TYPE_IDS
            for a in FIRST_ADJECTIVE_IDS
            for b in SECOND_ADJECTIVE_IDS
        }
        assert len(names) == 6 * 6 * 6
        assert not any("{" in name for name in names)
