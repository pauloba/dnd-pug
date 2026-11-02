"""Tests for the command-line interface, prompts and the whole
workflow.
"""

import random
import subprocess
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest

from dnd_worldgen.cli import (
    LANGUAGE_NAMES,
    ask_int,
    main,
    parse_args,
    resolve_options,
)
from dnd_worldgen.config import MAX_LEVEL, MAX_PLAYERS
from dnd_worldgen.generators.universe import generate_universe
from dnd_worldgen.i18n import Translator
from dnd_worldgen.models import (
    Character,
    GenerationOptions,
    Language,
    Universe,
)
from dnd_worldgen.rendering import PdfBackendError
from dnd_worldgen.rules.themes import THEME_IDS


class Script:
    """Scripted keyboard input that records every prompt it was
    asked.
    """

    def __init__(self, answers: Sequence[str]) -> None:
        self._answers: Iterator[str] = iter(answers)
        self.prompts: list[str] = []

    def __call__(self, prompt: str) -> str:
        self.prompts.append(prompt)
        try:
            return next(self._answers)
        except StopIteration:
            raise EOFError from None


def no_input(prompt: str) -> str:
    raise AssertionError(f"unexpected question: {prompt!r}")


class Recorder:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def __call__(self, text: str) -> None:
        self.lines.append(text)

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


class FakeRenderer:
    """Stands in for PdfRenderer: files hold the data they would
    render.
    """

    def __init__(self, translator: Translator) -> None:
        self.translator = translator

    def write_character_pdf(self, character: Character, path: Path) -> None:
        path.write_text(repr(character), encoding="utf-8")

    def write_universe_pdf(self, universe: Universe, path: Path) -> None:
        path.write_text(
            repr(universe) + self.translator.language.value, encoding="utf-8"
        )


def run(
    args: Sequence[str], answers: Sequence[str] | None = None
) -> tuple[int, Recorder, Script | None]:
    out = Recorder()
    script = Script(answers) if answers is not None else None
    code = main(
        list(args),
        input_fn=script if script else no_input,
        output_fn=out,
        renderer_factory=FakeRenderer,
    )
    return code, out, script


# ----------------------------------------------------------------
# ask_int


def test_ask_int_returns_a_valid_answer() -> None:
    assert ask_int("?", 4, 1, 8, input_fn=Script(["6"])) == 6


@pytest.mark.parametrize("answer", ["", "   "])
def test_ask_int_empty_answer_gives_the_default(answer: str) -> None:
    assert ask_int("?", 4, 1, 8, input_fn=Script([answer])) == 4


def test_ask_int_end_of_input_gives_the_default() -> None:
    assert ask_int("?", 4, 1, 8, input_fn=Script([])) == 4


@pytest.mark.parametrize("bad", ["0", "9", "-1", "abc", "2.5", "1e3"])
def test_ask_int_explains_and_asks_again(bad: str) -> None:
    out = Recorder()
    script = Script([bad, "7"])
    assert ask_int("Players: ", 4, 1, 8, input_fn=script, output_fn=out) == 7
    assert out.lines == ["Please enter a whole number between 1 and 8."]
    assert script.prompts == ["Players: ", "Players: "]


def test_ask_int_accepts_the_limits_and_surrounding_spaces() -> None:
    assert ask_int("?", 4, 1, 8, input_fn=Script([" 1 "])) == 1
    assert ask_int("?", 4, 1, 8, input_fn=Script(["8"])) == 8


def test_ask_int_stops_asking_when_the_input_ends_after_a_mistake() -> None:
    out = Recorder()
    assert ask_int("?", 4, 1, 8, input_fn=Script(["99"]), output_fn=out) == 4
    assert len(out.lines) == 1


# --------------------------------------------------------------
# parse_args


def test_no_flags_means_nothing_is_decided() -> None:
    args = parse_args([])
    assert (
        args.language,
        args.theme_id,
        args.players,
        args.level,
        args.seed,
    ) == (
        None,
        None,
        None,
        None,
        None,
    )
    assert args.output_dir == Path(".") and not args.no_prompt


def test_all_flags_are_parsed() -> None:
    args = parse_args(
        [
            "--lang", "ES",
            "--theme", "solarpunk",
            "--players", "5",
            "--level", "7",
            "--seed", "123",
            "--output-dir", "out",
            "--no-prompt",
        ]
    )  # fmt: skip
    assert args.language is Language.ES
    assert args.theme_id == "solarpunk"
    assert (args.players, args.level, args.seed) == (5, 7, 123)
    assert args.output_dir == Path("out") and args.no_prompt


@pytest.mark.parametrize("number", range(1, len(THEME_IDS) + 1))
def test_a_theme_can_be_given_as_its_menu_number(number: int) -> None:
    assert (
        parse_args(["--theme", str(number)]).theme_id == THEME_IDS[number - 1]
    )


@pytest.mark.parametrize(
    ("flags", "message"),
    [
        (["--players", "0"], "between 1 and 8"),
        (["--players", "9"], "between 1 and 8"),
        (["--players", "many"], "not a whole number"),
        (["--level", "0"], "between 1 and 20"),
        (["--level", "21"], "between 1 and 20"),
        (["--theme", "0"], f"between 1 and {len(THEME_IDS)}"),
        (
            ["--theme", str(len(THEME_IDS) + 1)],
            f"between 1 and {len(THEME_IDS)}",
        ),
        (["--theme", "atlantis"], "unknown theme 'atlantis'"),
        (["--lang", "klingon"], "unknown language 'klingon'"),
        (["--seed", "x"], "invalid int value"),
    ],
)
def test_bad_flags_exit_with_a_clear_message(
    flags: list[str], message: str, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as info:
        parse_args(flags)
    assert info.value.code == 2
    assert message in capsys.readouterr().err


def test_the_limits_in_the_flags_come_from_the_config() -> None:
    assert parse_args(["--players", str(MAX_PLAYERS)]).players == MAX_PLAYERS
    assert parse_args(["--level", str(MAX_LEVEL)]).level == MAX_LEVEL


# ---------------------------------------------------------
# resolve_options


def test_every_language_has_a_menu_name() -> None:
    assert set(LANGUAGE_NAMES) == set(Language)


def test_prompts_are_shown_in_the_original_order_and_wording() -> None:
    out, script = Recorder(), Script(["2", "6", "5", "4"])
    options = resolve_options(parse_args([]), script, out)
    assert script.prompts == [
        f"Choice [1-{len(Language)}] (Default 1): ",
        f"Theme Choice [1-{len(THEME_IDS)}] (Default 1): ",
        "Enter Number of Player Characters [1-8] (Default 4): ",
        "Enter Character Level [1-20] (Default 1): ",
    ]
    assert (options.language, options.theme_id) == (Language.ES, THEME_IDS[5])
    assert (options.num_players, options.character_level) == (5, 4)


def test_the_theme_menu_uses_the_chosen_language() -> None:
    out = Recorder()
    resolve_options(parse_args([]), Script(["2"]), out)
    spanish = Translator.load(Language.ES)
    assert f"1) {spanish.name('themes', THEME_IDS[0])}" in out.lines
    last = len(THEME_IDS)
    assert f"{last}) {spanish.name('themes', THEME_IDS[-1])}" in out.lines
    assert "1) English" in out.lines and "2) Español" in out.lines


def test_empty_answers_give_the_original_defaults() -> None:
    options = resolve_options(
        parse_args([]), Script(["", "", "", ""]), Recorder()
    )
    assert options == GenerationOptions(THEME_IDS[0], Language.EN, 4, 1)


def test_only_missing_settings_are_asked() -> None:
    script = Script(["3"])
    options = resolve_options(
        parse_args(["--lang", "en", "--theme", "2", "--level", "5"]),
        script,
        Recorder(),
    )
    assert script.prompts == [
        "Enter Number of Player Characters [1-8] (Default 4): "
    ]
    assert (
        options.theme_id,
        options.num_players,
        options.character_level,
    ) == (
        THEME_IDS[1],
        3,
        5,
    )


def test_no_prompt_uses_defaults_and_never_asks() -> None:
    options = resolve_options(
        parse_args(["--no-prompt", "--players", "2"]), no_input, Recorder()
    )
    assert options == GenerationOptions(THEME_IDS[0], Language.EN, 2, 1)


# -------------------------------------------------------------------
# main


def test_full_run_with_flags_only(tmp_path: Path) -> None:
    code, out, _ = run(
        ["--lang", "es", "--theme", "6", "--players", "3", "--level", "2",
         "--seed", "42", "--output-dir", str(tmp_path)]
    )  # fmt: skip
    assert code == 0
    assert sorted(p.name for p in (tmp_path / "game1").iterdir()) == [
        "character1.pdf",
        "character2.pdf",
        "character3.pdf",
        "game.pdf",
    ]
    assert "D&D PROCEDURAL UNIVERSE GENERATOR ENGINE" in out.text
    assert (
        "[Engine] Seed: 42 (use --seed 42 to reproduce this universe)"
        in out.text
    )
    assert f"[+] Created Output Directory: {tmp_path / 'game1'}/" in out.text
    assert (
        f"[+] World Manual Generated: {tmp_path / 'game1' / 'game.pdf'}"
        in out.text
    )
    assert out.text.count("[+] Player Sheet Generated:") == 3
    assert "[✓] Universe Generation Completed Successfully!" in out.text


def test_full_interactive_run(tmp_path: Path) -> None:
    code, out, script = run(
        ["--output-dir", str(tmp_path)], ["1", "2", "99", "2", "", ""]
    )
    assert code == 0 and script is not None
    assert "Please enter a whole number between 1 and 8." in out.lines
    assert len(list((tmp_path / "game1").glob("character*.pdf"))) == 2


def test_the_original_messages_come_in_the_original_order(
    tmp_path: Path,
) -> None:
    _, out, _ = run(
        ["--no-prompt", "--seed", "1", "--output-dir", str(tmp_path)]
    )
    markers = [
        "D&D PROCEDURAL UNIVERSE GENERATOR ENGINE",
        "[Engine] Synthesizing procedural world",
        "[+] Created Output Directory",
        "[+] World Manual Generated",
        "[+] Player Sheet Generated",
        "[✓] Universe Generation Completed Successfully!",
    ]
    positions = [out.text.index(marker) for marker in markers]
    assert positions == sorted(positions)


def test_files_hold_the_same_universe_as_the_generator(tmp_path: Path) -> None:
    run(["--theme", "3", "--lang", "en", "--players", "2", "--level", "1",
         "--seed", "9", "--output-dir", str(tmp_path)])  # fmt: skip
    expected = generate_universe(
        GenerationOptions(THEME_IDS[2], Language.EN, 2, 1),
        random.Random(9),
        Translator.load(Language.EN),
    )
    assert (tmp_path / "game1" / "game.pdf").read_text() == repr(
        expected
    ) + "en"
    assert (tmp_path / "game1" / "character2.pdf").read_text() == repr(
        expected.party[1]
    )


def test_the_same_seed_gives_the_same_files(tmp_path: Path) -> None:
    flags = ["--no-prompt", "--seed", "77"]
    run([*flags, "--output-dir", str(tmp_path / "a")])
    run([*flags, "--output-dir", str(tmp_path / "b")])
    for name in ("game.pdf", "character1.pdf", "character4.pdf"):
        assert (tmp_path / "a" / "game1" / name).read_text() == (
            tmp_path / "b" / "game1" / name
        ).read_text()


def test_a_random_seed_is_reported_and_reproduces_the_universe(
    tmp_path: Path,
) -> None:
    _, out, _ = run(["--no-prompt", "--output-dir", str(tmp_path / "a")])
    seed = next(
        line for line in out.lines if line.startswith("[Engine] Seed:")
    ).split()[2]
    run(["--no-prompt", "--seed", seed, "--output-dir", str(tmp_path / "b")])
    assert (tmp_path / "a" / "game1" / "game.pdf").read_text() == (
        tmp_path / "b" / "game1" / "game.pdf"
    ).read_text()


def test_runs_do_not_overwrite_each_other(tmp_path: Path) -> None:
    for _ in range(3):
        run(["--no-prompt", "--players", "1", "--output-dir", str(tmp_path)])
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "game1",
        "game2",
        "game3",
    ]


def test_a_missing_pdf_backend_gives_a_message_and_leaves_no_folder(
    tmp_path: Path,
) -> None:
    class Broken:
        def __init__(self, translator: Translator) -> None: ...

        def write_character_pdf(
            self, character: Character, path: Path
        ) -> None:
            raise PdfBackendError("PDF output needs WeasyPrint")

        def write_universe_pdf(self, universe: Universe, path: Path) -> None:
            raise PdfBackendError("PDF output needs WeasyPrint")

    out = Recorder()
    code = main(
        ["--no-prompt", "--output-dir", str(tmp_path)],
        input_fn=no_input,
        output_fn=out,
        renderer_factory=Broken,
    )
    assert code == 1
    assert "[!] PDF output needs WeasyPrint" in out.lines
    assert list(tmp_path.iterdir()) == []


# -------------------------------------------------- the real thing
# (PDFs)


def weasyprint_or_skip() -> None:
    try:
        import weasyprint  # noqa: F401
    except (ImportError, OSError):
        pytest.skip("WeasyPrint's system libraries are not available here")


def test_real_pdfs_are_written(tmp_path: Path) -> None:
    weasyprint_or_skip()
    out = Recorder()
    code = main(
        ["--lang", "es", "--theme", "6", "--players", "2", "--level", "3",
         "--seed", "42", "--output-dir", str(tmp_path)],
        input_fn=no_input,
        output_fn=out,
    )  # fmt: skip
    assert code == 0
    for name in ("game.pdf", "character1.pdf", "character2.pdf"):
        assert (tmp_path / "game1" / name).read_bytes().startswith(b"%PDF")


def test_python_dash_m_runs_the_cli(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "dnd_worldgen", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--players" in result.stdout and "--no-prompt" in result.stdout
