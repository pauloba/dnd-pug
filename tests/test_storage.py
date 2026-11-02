"""Tests for the numbered game folders and writing the PDF files."""

import random
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
from dnd_worldgen.storage import (
    character_pdf_name,
    create_game_dir,
    write_universe_files,
)


class FakeWriter:
    """Writes small text files instead of PDFs; can be told to fail."""

    def __init__(self, fail_on: str | None = None) -> None:
        self.fail_on = fail_on
        self.calls: list[str] = []

    def write_character_pdf(self, character: Character, path: Path) -> None:
        self._write(path, f"character {character.name}")

    def write_universe_pdf(self, universe: Universe, path: Path) -> None:
        self._write(path, f"universe {universe.universe_id}")

    def _write(self, path: Path, text: str) -> None:
        self.calls.append(path.name)
        if path.name == self.fail_on:
            raise RuntimeError("disk on fire")
        path.write_text(text, encoding="utf-8")


def make_universe(players: int = 3) -> Universe:
    options = GenerationOptions("steampunk", Language.EN, num_players=players)
    return generate_universe(
        options, random.Random(1), Translator.load(Language.EN)
    )


# ------------------------------------------------------------- game
# folders


def test_first_folder_is_game1(tmp_path: Path) -> None:
    folder = create_game_dir(tmp_path)
    assert folder == tmp_path / "game1" and folder.is_dir()


def test_folders_are_numbered_upwards(tmp_path: Path) -> None:
    names = [create_game_dir(tmp_path).name for _ in range(3)]
    assert names == ["game1", "game2", "game3"]


def test_gaps_are_reused_like_in_the_original(tmp_path: Path) -> None:
    for _ in range(3):
        create_game_dir(tmp_path)
    (tmp_path / "game1").rmdir()
    assert create_game_dir(tmp_path).name == "game1"
    assert create_game_dir(tmp_path).name == "game4"


def test_a_file_called_game1_is_skipped_too(tmp_path: Path) -> None:
    (tmp_path / "game1").write_text("not a folder")
    assert create_game_dir(tmp_path).name == "game2"


def test_missing_base_folders_are_created(tmp_path: Path) -> None:
    folder = create_game_dir(tmp_path / "deep" / "er")
    assert folder == tmp_path / "deep" / "er" / "game1"


def test_other_folders_are_left_alone(tmp_path: Path) -> None:
    (tmp_path / "notes").mkdir()
    (tmp_path / "game2").mkdir()
    assert create_game_dir(tmp_path).name == "game1"


# ------------------------------------------------------------- writing
# files


def test_file_names() -> None:
    assert character_pdf_name(1) == "character1.pdf"
    assert character_pdf_name(12) == "character12.pdf"


def test_every_character_and_the_universe_are_written(tmp_path: Path) -> None:
    universe = make_universe(players=3)
    game_dir = create_game_dir(tmp_path)
    files = write_universe_files(universe, FakeWriter(), game_dir)
    assert files.directory == game_dir
    assert [p.name for p in files.character_pdfs] == [
        "character1.pdf",
        "character2.pdf",
        "character3.pdf",
    ]
    assert files.universe_pdf == game_dir / "game.pdf"
    assert sorted(p.name for p in game_dir.iterdir()) == [
        "character1.pdf",
        "character2.pdf",
        "character3.pdf",
        "game.pdf",
    ]
    assert (game_dir / "character2.pdf").read_text() == (
        f"character {universe.party[1].name}"
    )


def test_characters_are_written_before_the_universe_like_the_original(
    tmp_path: Path,
) -> None:
    writer = FakeWriter()
    write_universe_files(make_universe(2), writer, create_game_dir(tmp_path))
    assert writer.calls == ["character1.pdf", "character2.pdf", "game.pdf"]


def test_an_empty_folder_is_removed_when_writing_fails_at_once(
    tmp_path: Path,
) -> None:
    game_dir = create_game_dir(tmp_path)
    with pytest.raises(RuntimeError, match="disk on fire"):
        write_universe_files(
            make_universe(), FakeWriter("character1.pdf"), game_dir
        )
    assert not game_dir.exists()
    assert (
        create_game_dir(tmp_path).name == "game1"
    )  # the number is free again


def test_files_already_written_are_kept_when_a_later_write_fails(
    tmp_path: Path,
) -> None:
    game_dir = create_game_dir(tmp_path)
    with pytest.raises(RuntimeError):
        write_universe_files(make_universe(), FakeWriter("game.pdf"), game_dir)
    assert sorted(p.name for p in game_dir.iterdir()) == [
        "character1.pdf",
        "character2.pdf",
        "character3.pdf",
    ]
