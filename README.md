# D&D Procedural Universe Generator

The current generator is in [`generator.py`](generator.py). 
It creates a complete campaign universe and printable PDF character sheets
from randomly selected D&D content.

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

- Language: English or Spanish. Spanish is the default.
- Theme: one of 9 settings. Solarpunk Arcane Canopy is the default theme.
- Number of characters: 1 to 10. The default is 3.

Invalid language and theme selections use their defaults. Character counts are constrained to the range 1–10; a blank or invalid count generates 3 characters.

## Generated content

Each run generates:

- A unique four-digit universe ID.
- Two randomly named factions.
- Five settlements associated with the selected theme.
- One of four extended campaign stories for that theme.
- Level 3 characters with names, races, classes, subclasses, backgrounds, alignments, descriptions, ability scores, modifiers, relevant skills, faction affiliations, and backstory hooks.
- Three theme-specific encounters: introductory, escalating, and boss battles, including locations, enemies, armor, loot, and a story unlock for the boss encounter.

## Output

The generator creates the next unused folder in the directory where it is run: `game1`, `game2`, and so on. Each folder contains:

- `game.pdf`: the universe manual, including the world overview, campaign conflict, factions, settlements, party roster, and encounter dossier.
- `character1.pdf`, `character2.pdf`, and so on: one character sheet per generated character.