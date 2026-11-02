"""Command-line entry point: flags, prompts and progress messages.

Every setting can be given as a flag; whatever is missing is asked
interactively (or defaulted with ``--no-prompt``). The workflow itself
is short: build options, generate the universe (pure data), create the
next ``gameN`` folder, write the PDFs.
"""

import argparse
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from dnd_worldgen.config import (
    DEFAULT_LEVEL,
    DEFAULT_PLAYERS,
    MAX_LEVEL,
    MAX_PLAYERS,
    MIN_LEVEL,
    MIN_PLAYERS,
)
from dnd_worldgen.generators.universe import generate_universe
from dnd_worldgen.i18n import Translator
from dnd_worldgen.models import GenerationOptions, Language
from dnd_worldgen.rendering import PdfBackendError, PdfRenderer
from dnd_worldgen.rules.themes import DEFAULT_THEME_ID, THEME_IDS
from dnd_worldgen.storage import (
    PdfWriter,
    create_game_dir,
    write_universe_files,
)

InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]
RendererFactory = Callable[[Translator], PdfWriter]

BANNER = "\n".join(
    [
        "=" * 50,
        "   D&D PROCEDURAL UNIVERSE GENERATOR ENGINE       ",
        "=" * 50,
    ]
)

#: How each language is named in the language menu (in its own
#: language).
LANGUAGE_NAMES = {Language.EN: "English", Language.ES: "Español"}
DEFAULT_LANGUAGE = Language.EN


@dataclass(frozen=True)
class CliArguments:
    """What was given on the command line.

    ``None`` means "not given".
    """

    language: Language | None
    theme_id: str | None
    players: int | None
    level: int | None
    seed: int | None
    output_dir: Path
    no_prompt: bool


# ------------------------------------------------------------------
# flags


def _language(text: str) -> Language:
    try:
        return Language(text.lower())
    except ValueError:
        choices = ", ".join(language.value for language in Language)
        raise argparse.ArgumentTypeError(
            f"unknown language {text!r} (choose from: {choices})"
        ) from None


def _theme(text: str) -> str:
    """Parse a theme given as a menu number (1-9) or as its ID.

    For example ``6`` or ``solarpunk``.
    """
    if text.isdigit():
        number = int(text)
        if 1 <= number <= len(THEME_IDS):
            return THEME_IDS[number - 1]
        raise argparse.ArgumentTypeError(
            f"theme number must be between 1 and {len(THEME_IDS)}"
        )
    if text in THEME_IDS:
        return text
    raise argparse.ArgumentTypeError(
        f"unknown theme {text!r} (use a number from 1 to {len(THEME_IDS)} "
        f"or one of: {', '.join(THEME_IDS)})"
    )


def _bounded_int(minimum: int, maximum: int) -> Callable[[str], int]:
    def parse(text: str) -> int:
        try:
            value = int(text)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"{text!r} is not a whole number"
            ) from None
        if not minimum <= value <= maximum:
            raise argparse.ArgumentTypeError(
                f"must be between {minimum} and {maximum}"
            )
        return value

    return parse


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser with every flag the CLI accepts."""
    parser = argparse.ArgumentParser(
        prog="dnd-worldgen",
        description=(
            "Generate a D&D universe manual and character sheets as PDFs. "
            "Anything not given as a flag is asked interactively."
        ),
    )
    parser.add_argument(
        "--lang",
        type=_language,
        metavar="{en,es}",
        help="output language (default: ask, English with --no-prompt)",
    )
    parser.add_argument(
        "--theme",
        type=_theme,
        metavar="THEME",
        help=(
            f"world theme: a number 1-{len(THEME_IDS)} or one of "
            f"{', '.join(THEME_IDS)}"
        ),
    )
    parser.add_argument(
        "--players",
        type=_bounded_int(MIN_PLAYERS, MAX_PLAYERS),
        metavar="N",
        help=f"number of player characters, {MIN_PLAYERS}-{MAX_PLAYERS}",
    )
    parser.add_argument(
        "--level",
        type=_bounded_int(MIN_LEVEL, MAX_LEVEL),
        metavar="N",
        help=f"character level, {MIN_LEVEL}-{MAX_LEVEL}",
    )
    parser.add_argument(
        "--seed",
        type=int,
        metavar="N",
        help="random seed: the same seed and settings give the same universe",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        metavar="DIR",
        help="where the gameN folder is created (default: current directory)",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="never ask questions: use the defaults for anything not given",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> CliArguments:
    """Parse command-line arguments into a :class:`CliArguments`."""
    namespace = build_parser().parse_args(argv)
    return CliArguments(
        language=namespace.lang,
        theme_id=namespace.theme,
        players=namespace.players,
        level=namespace.level,
        seed=namespace.seed,
        output_dir=namespace.output_dir,
        no_prompt=namespace.no_prompt,
    )


# ----------------------------------------------------------------
# prompts


def ask_int(
    prompt: str,
    default: int,
    minimum: int,
    maximum: int,
    *,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
) -> int:
    """Ask for a whole number in ``[minimum, maximum]``.

    An empty answer, or the end of the input, gives the default.
    Anything else that is not valid is explained and asked again.
    """
    while True:
        try:
            answer = input_fn(prompt).strip()
        except EOFError:
            return default
        if not answer:
            return default
        try:
            value = int(answer)
        except ValueError:
            value = (
                minimum - 1
            )  # not a number: reported like an out-of-range one
        if minimum <= value <= maximum:
            return value
        output_fn(
            f"Please enter a whole number between {minimum} and {maximum}."
        )


def ask_language(input_fn: InputFn, output_fn: OutputFn) -> Language:
    """Show the language menu and return the chosen language."""
    languages = list(Language)
    output_fn("Select Language / Seleccione el Idioma:")
    for number, language in enumerate(languages, start=1):
        output_fn(f"{number}) {LANGUAGE_NAMES[language]}")
    choice = ask_int(
        f"Choice [1-{len(languages)}] (Default 1): ",
        default=1,
        minimum=1,
        maximum=len(languages),
        input_fn=input_fn,
        output_fn=output_fn,
    )
    return languages[choice - 1]


def ask_theme(
    translator: Translator, input_fn: InputFn, output_fn: OutputFn
) -> str:
    """Show the theme menu and return the chosen theme ID.

    The names are shown in the chosen language.
    """
    output_fn("\nSelect World Theme / Seleccione el Tema del Mundo:")
    for number, theme_id in enumerate(THEME_IDS, start=1):
        output_fn(f"{number}) {translator.name('themes', theme_id)}")
    choice = ask_int(
        f"Theme Choice [1-{len(THEME_IDS)}] (Default 1): ",
        default=1,
        minimum=1,
        maximum=len(THEME_IDS),
        input_fn=input_fn,
        output_fn=output_fn,
    )
    return THEME_IDS[choice - 1]


def resolve_options(
    args: CliArguments, input_fn: InputFn, output_fn: OutputFn
) -> GenerationOptions:
    """Combine the flags with answers for whatever is missing."""
    ask = not args.no_prompt

    language = args.language
    if language is None:
        language = (
            ask_language(input_fn, output_fn) if ask else DEFAULT_LANGUAGE
        )

    theme_id = args.theme_id
    if theme_id is None:
        theme_id = (
            ask_theme(Translator.load(language), input_fn, output_fn)
            if ask
            else DEFAULT_THEME_ID
        )

    players = args.players
    if players is None:
        players = DEFAULT_PLAYERS
        if ask:
            players = ask_int(
                f"Enter Number of Player Characters "
                f"[{MIN_PLAYERS}-{MAX_PLAYERS}] (Default {DEFAULT_PLAYERS}): ",
                DEFAULT_PLAYERS,
                MIN_PLAYERS,
                MAX_PLAYERS,
                input_fn=input_fn,
                output_fn=output_fn,
            )

    level = args.level
    if level is None:
        level = DEFAULT_LEVEL
        if ask:
            level = ask_int(
                f"Enter Character Level [{MIN_LEVEL}-{MAX_LEVEL}] "
                f"(Default {DEFAULT_LEVEL}): ",
                DEFAULT_LEVEL,
                MIN_LEVEL,
                MAX_LEVEL,
                input_fn=input_fn,
                output_fn=output_fn,
            )

    return GenerationOptions(
        theme_id=theme_id,
        language=language,
        num_players=players,
        character_level=level,
        seed=args.seed,
    )


# -------------------------------------------------------------------
# main


def main(
    argv: Sequence[str] | None = None,
    *,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
    renderer_factory: RendererFactory = PdfRenderer,
) -> int:
    """Run the generator and return the process exit code.

    ``input_fn``, ``output_fn`` and ``renderer_factory`` exist so tests
    can run the whole workflow without a terminal or WeasyPrint.
    """
    args = parse_args(argv)
    output_fn(BANNER)
    options = resolve_options(args, input_fn, output_fn)

    seed = options.seed
    if seed is None:
        seed = random.SystemRandom().randrange(2**32)
    translator = Translator.load(options.language)

    output_fn(
        "\n[Engine] Synthesizing procedural world, lore chronicle, "
        "encounters, and character sheets..."
    )
    output_fn(
        f"[Engine] Seed: {seed} (use --seed {seed} to reproduce this universe)"
    )
    universe = generate_universe(options, random.Random(seed), translator)

    writer = renderer_factory(translator)
    game_dir = create_game_dir(args.output_dir)
    output_fn(f"\n[+] Created Output Directory: {game_dir}/")
    try:
        files = write_universe_files(universe, writer, game_dir)
    except PdfBackendError as error:
        output_fn(f"[!] {error}")
        return 1

    output_fn(f"[+] World Manual Generated: {files.universe_pdf}")
    for path in files.character_pdfs:
        output_fn(f"[+] Player Sheet Generated: {path}")
    output_fn("[✓] Universe Generation Completed Successfully!\n")
    return 0
