# D&D Procedural Universe Generator

The generator creates a complete campaign universe and printable PDF character
sheets from randomly selected D&D content.

## Requirements

Install the Python dependency used to render the PDFs:

```
pip install -r requirements.txt
```

## Run the generator

Run the command from the `root` directory:

```
python3 generator.py
```

The interactive prompts ask for:

- Language: English or Spanish. English is the default.
- Theme: one of 9 settings. High Fantasy Steampunk is the default theme.
- Number of characters: 1 to 8. The default is 4.
- Character level: a positive integer shared by all generated characters. The default is 1.

Invalid language and theme selections use their defaults. Character counts are constrained to the range 1–8; a blank or invalid count generates 4 characters. A blank, invalid, or non-positive character level generates level 1 characters.

## Generated content

Each run generates:

- A randomly generated four-digit universe ID, prefixed with `UNI-`.
- Three randomly named factions.
- Three settlements associated with the selected theme.
- One of four extended campaign stories for that theme.
- Characters at the selected level with names, races, classes, subclasses, backgrounds, alignments, descriptions, ability scores, modifiers, relevant skills, faction affiliations, and backstory hooks.
- A separate subclass field on character sheets for characters at level 3 or above; levels 1 and 2 retain the standard character-sheet layout.
- Three theme-specific encounters: introductory, escalating, and boss battles, including locations, enemies, armor, loot, and a story unlock for the boss encounter.

## How it works

There are 9 themes, with 4 campaign stories per theme. English and Spanish
each contain 36 localized story variants, representing 36 story concepts.

The battles are fixed per theme and language rather than procedurally
randomized. Each theme has three encounters: an introductory battle, an
escalating battle, and a final boss battle.

The available themes are:

1. High Fantasy Steampunk
2. Post-Apocalyptic Arcana
3. Gothic Sunless Ocean
4. Shattered Floating Isles
5. Ancient Sun-Drenched Desert
6. Solarpunk Arcane Canopy
7. Covenstead & Warlock Pactlands
8. Sanguine Aristocracy & Vampire Courts
9. Silk Route Silk & Spice Merchant Empires

## Output

The generator creates the next unused folder in the directory where it is run: `game1`, `game2`, and so on. Each folder contains:

- `game.pdf`: the universe manual that serves as a guide for the Dungeon Master, including the world overview, campaign conflict, factions, settlements, party roster, and encounter dossier.
- `character1.pdf`, `character2.pdf`, and so on: one character sheet per generated character.
