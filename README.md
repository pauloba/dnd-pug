# DND-PUG

A procedural **D&D universe and character generator**. It writes a
universe manual (`game.pdf`) and one PDF character sheet per player,
in English or Spanish, in nine world themes (high-fantasy steampunk,
solarpunk, gothic, vampire courts, and more).

Each universe has factions, settlements, a campaign story, a three-stage
encounter dossier (low, mid and boss) and a ready-made party. The same
seed and settings always give the same universe.

## Installation

Python 3.10 or newer.

```bash
bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

PDF output uses [WeasyPrint](https://weasyprint.org/), which needs some
system libraries (Pango and friends). If the first PDF fails with a
message about WeasyPrint, follow the
[WeasyPrint install guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).
Everything except writing the PDF itself works without them.

## Usage

```bash
python -m dnd_worldgen                 # asks for everything
dnd-worldgen --lang es --theme 6 --players 4 --level 3 --seed 42
```

Every setting can be a flag; whatever is missing is asked interactively.
An invalid answer is explained and asked again, and an empty answer
takes the default.

| Flag | Meaning |
|---|---|
| `--lang {en,es}` | output language |
| `--theme THEME` | a number 1-9, or a name such as `solarpunk` (see `--help`) |
| `--players N` | player characters, 1-8 (default 4) |
| `--level N` | character level, 1-20 (default 1) |
| `--seed N` | the same seed and settings give the same universe |
| `--output-dir DIR` | where the `gameN` folder is created (default: here) |
| `--no-prompt` | never ask: use the defaults for anything not given |

Each run creates the next free folder (`game1`, `game2`, ...) containing
`game.pdf` (the universe manual) and `character1.pdf`,
`character2.pdf`, ... The seed used is printed, so a run you liked can be
reproduced with `--seed`.

## How it works

Generation, translation and rendering are separate steps:

1. **Rules** (`rules/`) hold IDs and numbers only: `fighter`, hit die 10,
   `chain_mail`. Nothing in them is language-specific.
2. **Generators** (`generators/`) roll dice with a seeded
   `random.Random` and produce plain data (`models.py`): frozen
   dataclasses that contain IDs and numbers, never translated text.
3. **Locale files** (`i18n/locales/<lang>/*.json`) hold every piece of
   text, keyed by those IDs. `Translator.t("classes.fighter.name")`
   looks one up.
4. **Rendering** (`rendering/`) turns the data into display text (view
   models), fills the Jinja2 templates and writes PDFs with WeasyPrint.
5. **The CLI** (`cli.py`, `storage.py`) asks questions, runs the steps
   and numbers the output folders.

Because the data has no language, one generated universe can be rendered
in any language, and adding a language never touches the generators.

## Project layout

```
src/dnd_worldgen/
├── cli.py            command-line flags, prompts and the main workflow
├── config.py         limits and defaults (players, levels, world size)
├── models.py         the data: Character, Universe, GenerationOptions...
├── storage.py        gameN folders and PDF file names
├── rules/            language-neutral game data (IDs and numbers)
├── generators/       dice, characters, factions, story, encounters,
│                     and universe.py which assembles them
├── i18n/             Translator, display helpers and the locale files
└── rendering/        view models, Jinja2 templates, CSS, PDF writer
tests/                one test module per area
docs/                 the refactoring plan and its history
```

## Adding a language

1. Add a member to `Language` in `models.py` (the value is the locale
   folder name, for example `FR = "fr"`) and a menu name for it in
   `LANGUAGE_NAMES` in `cli.py`.
2. Copy `i18n/locales/en/` to `i18n/locales/fr/` and translate the
   values in every file. **Keep the keys (the IDs) and the placeholders
   such as `{faction}` exactly as they are.**
3. Run `pytest`. The tests list everything still missing or inconsistent
   (a missing key, a different placeholder, an empty text, a story
   without its paragraphs), and `--lang fr` then works.

Word order can differ between languages: faction names are built from
the pattern in `factions.json` (`name_pattern`), so a language can put
the type first or last.

## Adding a theme

1. Choose an ID (lowercase letters, digits and underscores) and append it
   to `THEME_IDS` in `rules/themes.py`. Appending keeps the existing
   menu numbers.
2. Give it at least three settlement IDs in `SETTLEMENT_IDS_BY_THEME`
   (`rules/themes.py`), its story IDs in `rules/stories.py`, and its
   three encounters in `rules/encounters.py`.
3. In **every** language folder, add the text: the theme name
   (`themes.json`), the settlements (`settlements.json`), a pool of
   character names (`names.json`; six is the convention), the stories
   (`stories.json`, three paragraphs each) and the encounter locations,
   enemies and boss unlock (`encounters.json`).
4. Run `pytest`. The coverage tests tell you which entry is missing.

## Development

```bash
ruff check .          # lint: PEP 8, naming, imports, docstrings (PEP 257)
black --check .       # formatting
mypy                  # strict type checking
pytest                # the test suite
```

The code follows [PEP 8](https://peps.python.org/pep-0008/) strictly (79
columns for code, 72 for comments and docstrings), has a docstring on
every public item, and is fully type-annotated. `ruff` and `black` are
configured in `pyproject.toml`.

## Refactoring

This project began as a single 2,600-line script. 
The goal was to make it more readable, maintainable, PEP 8 compliant, language-neutral core, easy to add new languages and themes.
It was rebuilt step by step, and each step was compared against the original: 
the data tables rebuilt losslessly from the new files; 
6,000 characters and 2,880 universes identical field by field; 
360 generated documents identical in structure and 
text and 30 identical pixel for pixel; 
and the new command line identical to the original interactive script 
on 18 real PDFs.

## Known limitations

- **The character sheet runs onto a second page.** Only its last few
  lines do. The original script behaved the same way; fixing it means a
  small layout change (tighter margins or spacing).
- **The interface text** (banner, prompts, progress messages) is in
  English only, whatever the output language.
- Pytest may print a WeasyPrint warning about `HarfBuzz-Subset`. It is
  harmless: an optional system library that future WeasyPrint versions
  will want.
