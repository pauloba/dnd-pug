"""Lookup of translated text by dotted key.

Locale files live in ``locales/<language>/<file>.json``. The first part
of a key is the file name, the rest walks into the JSON::

    translator.t("classes.fighter.name")
    translator.t("hooks.hook_1", faction="...")
    translator.strings("names.steampunk")

The first call reads ``classes.json``, the second fills the
``{faction}`` placeholder of a template and the third returns a list
of strings.

IDs never contain dots (``tests/test_rules_data.py`` enforces this), so
a dot is always a separator.
"""

import difflib
import json
from collections.abc import Mapping
from functools import cache
from importlib import resources
from typing import Any

from dnd_worldgen.models import Language

#: Parsed locale files for one language: ``{file name without .json:
#: content}``.
Catalog = Mapping[str, Any]


class TranslationError(KeyError):
    """A translation is missing or cannot be used as requested.

    Subclasses ``KeyError`` so ``except KeyError`` still works, but
    prints its message normally instead of as a quoted ``repr``.
    """

    def __str__(self) -> str:
        """Return the message without KeyError's extra quotes."""
        return str(self.args[0])


@cache
def load_catalog(language: Language) -> Catalog:
    """Read every JSON file of a language, once.

    The result is shared: treat it as read-only.
    """
    folder = resources.files("dnd_worldgen.i18n") / "locales" / language.value
    catalog: dict[str, Any] = {}
    for entry in sorted(folder.iterdir(), key=lambda item: item.name):
        if entry.name.endswith(".json"):
            name = entry.name.removesuffix(".json")
            catalog[name] = json.loads(entry.read_text(encoding="utf-8"))
    return catalog


class Translator:
    """Resolves dotted keys to text in one language."""

    def __init__(self, language: Language, catalog: Catalog) -> None:
        """Create a translator from an already loaded ``catalog``."""
        self._language = language
        self._catalog = catalog

    @classmethod
    def load(cls, language: Language) -> "Translator":
        """Create a translator backed by the packaged locale files."""
        return cls(language, load_catalog(language))

    @property
    def language(self) -> Language:
        """The language this translator speaks."""
        return self._language

    # -------------------------------------------------------------
    # lookups

    def get(self, key: str) -> Any:
        """Return the raw value at ``key`` (text, list or section)."""
        node: Any = self._catalog
        walked: list[str] = []
        for part in key.split("."):
            if not isinstance(node, Mapping) or part not in node:
                raise self._missing(key, walked, part, node)
            node = node[part]
            walked.append(part)
        return node

    def has(self, key: str) -> bool:
        """Whether ``key`` exists."""
        try:
            self.get(key)
        except TranslationError:
            return False
        return True

    def t(self, key: str, /, **params: object) -> str:
        """Return the text at ``key``.

        With keyword arguments the text is treated as a template and
        filled with ``str.format``; extra arguments are ignored (some
        hooks only use ``{faction}``). Without them the text is returned
        untouched.
        """
        node = self.get(key)
        if not isinstance(node, str):
            raise TranslationError(
                f"Translation {key!r} ({self._language.value}) is a "
                f"{type(node).__name__}, not text. Use get() or strings()."
            )
        if not params:
            return node
        try:
            return node.format(**params)
        except (KeyError, IndexError, ValueError) as error:
            raise TranslationError(
                f"Translation {key!r} ({self._language.value}) could not be "
                f"filled with parameters {sorted(params)}: {error!r}"
            ) from error

    def strings(self, key: str) -> tuple[str, ...]:
        """Return the list of strings at ``key``.

        For example a pool of names.
        """
        node = self.get(key)
        if not isinstance(node, list) or not all(
            isinstance(s, str) for s in node
        ):
            raise TranslationError(
                f"Translation {key!r} ({self._language.value}) is not a "
                "list of text."
            )
        return tuple(node)

    def name(self, category: str, item_id: str) -> str:
        """Display name of an ID, e.g. ``name("classes", "fighter")``.

        Works for both layouts: plain text entries (themes, skills,
        settlements) and ``{name, description}`` entries (classes,
        races, ...).
        """
        node = self.get(f"{category}.{item_id}")
        if isinstance(node, str):
            return node
        return self.t(f"{category}.{item_id}.name")

    def description(self, category: str, item_id: str) -> str:
        """Return the description of an ID.

        For example ``description("races", "elf")``.
        """
        return self.t(f"{category}.{item_id}.description")

    # --------------------------------------------------------------
    # errors

    def _missing(
        self, key: str, walked: list[str], part: str, node: Any
    ) -> TranslationError:
        where = ".".join(walked) or "the catalog"
        if not isinstance(node, Mapping):
            reason = f"{where!r} is a value, not a section"
        else:
            reason = f"{part!r} not found in {where!r}"
            close = difflib.get_close_matches(
                part, [str(k) for k in node], n=3
            )
            if close:
                reason += f" (did you mean {', '.join(map(repr, close))}?)"
        return TranslationError(
            f"Missing translation {key!r} for language "
            f"{self._language.value!r}: {reason}"
        )
