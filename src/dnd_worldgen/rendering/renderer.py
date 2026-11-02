"""Turn generated models into HTML (Jinja2) and PDF files (WeasyPrint).

HTML rendering and PDF writing are separate steps: the ``render_*_html``
methods return a string and need nothing but Jinja2, so they are easy to
test. WeasyPrint (which needs system libraries) is only imported when a
PDF is actually written.
"""

from functools import cache
from importlib import resources
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, StrictUndefined

from dnd_worldgen.generators.stats import format_modifier
from dnd_worldgen.i18n import Translator
from dnd_worldgen.models import Character, Universe
from dnd_worldgen.rendering.views import (
    build_character_view,
    build_universe_view,
)


@cache
def read_css(*names: str) -> str:
    """Return the CSS files of the templates folder, joined.

    They are joined in the order given.
    """
    folder = resources.files("dnd_worldgen.rendering") / "templates"
    return "\n".join(
        (folder / name).read_text(encoding="utf-8") for name in names
    )


class PdfBackendError(RuntimeError):
    """WeasyPrint is not installed or cannot load its libraries."""


def html_to_pdf(html: str, path: Path) -> None:
    """Write an HTML document to a PDF file."""
    try:
        from weasyprint import HTML  # imported here: it needs system libraries
    except (ImportError, OSError) as error:
        raise PdfBackendError(
            "PDF output needs WeasyPrint and its system libraries (Pango). "
            "See the README for installation help."
        ) from error

    HTML(string=html).write_pdf(path)


class PdfRenderer:
    """Renders universes and characters in the translator's language."""

    def __init__(self, translator: Translator) -> None:
        """Set up the Jinja environment for one language."""
        self._translator = translator
        self._env = Environment(
            loader=PackageLoader("dnd_worldgen.rendering", "templates"),
            # Every template is HTML. The `.j2` suffix would defeat the
            # default of select_autoescape(), so escaping is forced on.
            autoescape=True,
            # A typo in a template is an error, not blank text.
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._env.filters["signed"] = format_modifier

    def _render(self, template: str, page_css: str, **context: Any) -> str:
        return self._env.get_template(template).render(
            lang=self._translator.language.value,
            labels=self._translator.get("labels"),
            css=read_css("base.css", page_css),
            **context,
        )

    def render_character_html(self, character: Character) -> str:
        """Return the character sheet as an HTML document."""
        view = build_character_view(self._translator, character)
        return self._render(
            "character.html.j2", "character.css", character=view
        )

    def render_universe_html(self, universe: Universe) -> str:
        """Return the universe manual as an HTML document."""
        view = build_universe_view(self._translator, universe)
        return self._render("universe.html.j2", "universe.css", universe=view)

    def write_character_pdf(self, character: Character, path: Path) -> None:
        """Write a character sheet to ``path`` as a PDF."""
        html_to_pdf(self.render_character_html(character), path)

    def write_universe_pdf(self, universe: Universe, path: Path) -> None:
        """Write the universe manual to ``path`` as a PDF."""
        html_to_pdf(self.render_universe_html(universe), path)
