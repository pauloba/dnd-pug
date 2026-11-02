"""Where generated files go: game folders and PDF file names."""

import contextlib
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from dnd_worldgen.models import Character, Universe

GAME_FOLDER_PREFIX = "game"
UNIVERSE_PDF_NAME = "game.pdf"


def character_pdf_name(number: int) -> str:
    """File name of the ``number``-th character sheet (1-based)."""
    return f"character{number}.pdf"


class PdfWriter(Protocol):
    """Anything that can write the two kinds of PDF.

    ``PdfRenderer`` does.
    """

    def write_universe_pdf(self, universe: Universe, path: Path) -> None:
        """Write the universe manual to ``path``."""

    def write_character_pdf(self, character: Character, path: Path) -> None:
        """Write one character sheet to ``path``."""


@dataclass(frozen=True)
class WrittenFiles:
    """The files one generation run produced."""

    directory: Path
    universe_pdf: Path
    character_pdfs: tuple[Path, ...]


def create_game_dir(base_dir: Path) -> Path:
    """Create and return the lowest free ``gameN`` folder.

    It is created inside ``base_dir``.

    Like the original, gaps are reused (``game1`` is picked again if it
    was deleted while ``game2`` still exists). Creating the folder is
    the check, so two runs at the same moment cannot pick the same one.
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    number = 1
    while True:
        candidate = base_dir / f"{GAME_FOLDER_PREFIX}{number}"
        try:
            candidate.mkdir()
        except FileExistsError:
            number += 1
        else:
            return candidate


def write_universe_files(
    universe: Universe, writer: PdfWriter, game_dir: Path
) -> WrittenFiles:
    """Write the character sheets, then the universe manual.

    Everything goes into ``game_dir``.

    If writing fails before anything was written, the empty folder is
    removed again; files already written stay where they are.
    """
    try:
        character_pdfs = []
        for number, character in enumerate(universe.party, start=1):
            path = game_dir / character_pdf_name(number)
            writer.write_character_pdf(character, path)
            character_pdfs.append(path)
        universe_pdf = game_dir / UNIVERSE_PDF_NAME
        writer.write_universe_pdf(universe, universe_pdf)
    except BaseException:
        with contextlib.suppress(OSError):
            game_dir.rmdir()  # only succeeds while the folder is empty
        raise
    return WrittenFiles(game_dir, universe_pdf, tuple(character_pdfs))
