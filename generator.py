# -*- coding: utf-8 -*-
"""
D&D Procedural Universe & Character Generator Engine
Generates customized PDFs for D&D Universes (game.pdf) and Player Characters (character1.pdf, etc.)
Outputs to an auto-incrementing game folder (game1, game2, etc.)
Includes Solarpunk setting, extended narrative stories, encounter/enemy generation, and interactive terminal prompts.
"""

import json
import os
import random
from typing import Any, Dict, List
from weasyprint import HTML

# ==========================================
# DATA TABLES (ENGLISH & SPANISH)
# ==========================================

DATA_EN = {
    "themes": {
        "1": "High Fantasy Steampunk",
        "2": "Post-Apocalyptic Arcana",
        "3": "Gothic Sunless Ocean",
        "4": "Shattered Floating Isles",
        "5": "Ancient Sun-Drenched Desert",
        "6": "Solarpunk Arcane Canopy",
        "7": "Covenstead & Warlock Pactlands",
        "8": "Sanguine Aristocracy & Vampire Courts",
        "9": "Silk Route Silk & Spice Merchant Empires",
    },
    "faction_types": [
        "Guild",
        "Cult",
        "Empire",
        "Rebel Syndicate",
        "Circle of Druids",
        "Eco-Engineers Alliance",
    ],
    "faction_adjectives_1": [
        "Iron",
        "Golden",
        "Shadowed",
        "Arcane",
        "Celestial",
        "Verdant",
    ],
    "faction_adjectives_2": [
        "Crimson",
        "Silent",
        "Boundless",
        "Verdant",
        "Ebon",
        "Solar",
    ],
    "alignments": [
        "Lawful Good", "Neutral Good", "Chaotic Good",
        "Lawful Neutral", "True Neutral", "Chaotic Neutral",
        "Lawful Evil", "Neutral Evil", "Chaotic Evil"
    ],
    "alignment_descriptions": {
        "Lawful Good": "Combines honor and compassion, acting with tradition and moral integrity to protect others.",
        "Neutral Good": "Guided by conscience to do the right thing, helping others regardless of rules or authority.",
        "Chaotic Good": "Follows a personal moral compass toward freedom and kindness, rebelling against tyranny.",
        "Lawful Neutral": "Acts according to law, order, custom, or personal codes without bias toward good or evil.",
        "True Neutral": "Prefers balance over dogma, avoiding strong commitments to law, chaos, good, or evil.",
        "Chaotic Neutral": "Values absolute personal freedom above all else, following whim without malice or altruism.",
        "Lawful Evil": "Methodically uses laws, order, or authority to manipulate systems and advance selfish goals.",
        "Neutral Evil": "Purely self-serving, doing whatever it takes to gain power without honor or senseless mayhem.",
        "Chaotic Evil": "Driven by wild desires and destruction, showing total disregard for order, life, or rules."
    },
    "races": [
        "Human",
        "Elf",
        "Dwarf",
        "Halfling",
        "Tiefling",
        "Dragonborn",
        "Gnome",
        "Half-Orc",
    ],
    "classes": [
        "Fighter",
        "Wizard",
        "Rogue",
        "Cleric",
        "Ranger",
        "Paladin",
        "Bard",
        "Druid",
        "Warlock",
    ],
    "subclasses": {
        "Fighter": ["Champion", "Battle Master", "Eldritch Knight"],
        "Wizard": ["School of Evocation", "School of Abjuration", "School of Divination"],
        "Rogue": ["Thief", "Assassin", "Arcane Trickster"],
        "Cleric": ["Life Domain", "Light Domain", "War Domain"],
        "Ranger": ["Hunter", "Beast Master", "Gloom Stalker"],
        "Paladin": ["Oath of Devotion", "Oath of the Ancients", "Oath of Vengeance"],
        "Bard": ["College of Lore", "College of Valor", "College of Glamour"],
        "Druid": ["Circle of the Land", "Circle of the Moon", "Circle of Stars"],
        "Warlock": ["The Fiend", "The Great Old One", "The Archfey"],
    },
    "subclass_descriptions": {
        "Champion": "Focuses on raw physical power, refining attacks to deal devastating critical strikes.",
        "Battle Master": "Employs tactical maneuvers and precision superiority dice to command the battlefield.",
        "Eldritch Knight": "Combines martial prowess with abjuration and evocation magic for versatility.",
        "School of Evocation": "Master of elemental forces, shaping powerful destructive spells around allies.",
        "School of Abjuration": "Specializes in protective wards, counterspells, and defensive magic.",
        "School of Divination": "Glimpses into the future to alter fate, foreseeing outcomes before they happen.",
        "Thief": "Enhances agility and stealth, expertly picking locks and using items in the heat of action.",
        "Assassin": "Master of surprise attacks, disguise, and deadly poisons delivered from the shadows.",
        "Arcane Trickster": "Enhances rogue stealth with illusion and enchantment spells to deceive foes.",
        "Life Domain": "Channeler of divine energy focused on restoring health and preserving life.",
        "Light Domain": "Wields divine fire and radiant blinding light to scorch dark monstrosities.",
        "War Domain": "A holy warrior champion inspiring martial excellence and guided strikes.",
        "Hunter": "Specialized in combating hordes or giant beasts through specialized combat tactics.",
        "Beast Master": "Forms a deep bond with a loyal wild beast companion who fights by their side.",
        "Gloom Stalker": "A dark wilderness ambusher at home in deep shadows and underdark caverns.",
        "Oath of Devotion": "Embodies the ideal of the knight in shining armor, bound by honor and justice.",
        "Oath of the Ancients": "Fights for light and nature, preserving life, beauty, and ancient growth.",
        "Oath of Vengeance": "A ruthless punisher who hunts down transgressors and exacts retribution.",
        "College of Lore": "Gathers knowledge and secrets from all fields, weaving cutting words and extra spells.",
        "College of Valor": "Sings epic sagas to inspire allies in martial combat while wielding heavy armor.",
        "College of Glamour": "Channels fey magic to enthrall audiences and command respect with mesmerizing grace.",
        "Circle of the Land": "Preserves ancient nature lore and draws power directly from specific wilderness terrains.",
        "Circle of the Moon": "Master of wild shapes, transforming into powerful elemental beasts in combat.",
        "Circle of Stars": "Harnesses celestial constellations to channel radiant light and cosmic fates.",
        "The Fiend": "Bound to a lower-planar demon or devil, gaining fire magic and dark vitality.",
        "The Great Old One": "Gains eldritch mind-bending powers from alien entities beyond the stars.",
        "The Archfey": "Wields whimsical and deceptive fey magic to charm, frighten, and teleport.",
    },
    "skills_by_attr": {
        "STR": ["Athletics"],
        "DEX": ["Acrobatics", "Sleight of Hand", "Stealth"],
        "CON": [],
        "INT": ["Arcana", "History", "Investigation", "Nature", "Religion"],
        "WIS": ["Animal Handling", "Insight", "Medicine", "Perception", "Survival"],
        "CHA": ["Deception", "Intimidation", "Performance", "Persuasion"]
    },
    "backgrounds": [
        "Acolyte",
        "Criminal",
        "Folk Hero",
        "Noble",
        "Sage",
        "Soldier",
        "Urchin",
        "Outlander",
    ],
    "race_descriptions": {
        "Human": "Versatile and ambitious, humans are adaptable survivors who thrive in almost any environment.",
        "Elf": "Magical, long-lived beings with a deep connection to nature, grace, and ancient wisdom.",
        "Dwarf": "Bold, hardy, and resilient warriors and crafters shaped by deep mountain halls.",
        "Halfling": "Small and cheerful folk whose surprising luck and stealth often outshine their modest size.",
        "Tiefling": "Carrying an infernal heritage, tieflings navigate the world with fiery resolve and charisma.",
        "Dragonborn": "Proud dragon-descendants who honor heritage, honor, and raw elemental breath.",
        "Gnome": "Energetic and intensely curious inventors and tricksters driven by enthusiastic passion.",
        "Half-Orc": "Fierce combatants possessing unstoppable tenacity, physical power, and iron endurance.",
    },
    "class_descriptions": {
        "Fighter": "A master of martial combat, skilled with a variety of weapons and defensive armor.",
        "Wizard": "A scholarly magic-user capable of manipulating structures of reality via arcane spells.",
        "Rogue": "A scoundrel who uses stealth, precision, and agility to exploit enemy vulnerabilities.",
        "Cleric": "A priestly champion who wields divine magic in service of a higher power or deity.",
        "Ranger": "A warrior of the wilderness, tracking foes and mastering survival and martial skills.",
        "Paladin": "A holy warrior bound to a sacred oath, combining divine magic with heavy armor.",
        "Bard": "An inspiring performer whose music and words weave subtle weaves of magical force.",
        "Druid": "A priest of the Old Faith, drawing upon primeval nature powers and elemental forms.",
        "Warlock": "A seeker of esoteric knowledge who struck a pact with an otherworldly entity.",
    },
    "background_descriptions": {
        "Acolyte": "Spent years in service at a temple, acting as an intermediary between mortal life and the divine.",
        "Criminal": "A seasoned lawbreaker with a history of illicit dealings and underworld contacts.",
        "Folk Hero": "A champion of the common people whose courage stands against oppression and danger.",
        "Noble": "Born into wealth and privilege, accustomed to influence, high societal expectations, and power.",
        "Sage": "A dedicated scholar who spent years gathering lore, research, and ancient knowledge.",
        "Soldier": "Trained in tactical warfare, disciplined combat tactics, and military life on the battlefield.",
        "Urchin": "Grew up poor and homeless, relying on quick wits and street instincts to survive.",
        "Outlander": "Raised in the wild far from civilization, expert in survival, tracking, and nature.",
    },
    "settlements": {
        "High Fantasy Steampunk": [
            "Cogford",
            "Brassridge",
            "Aether-Spire",
            "Iron-Haven",
            "Steam-Gallow",
        ],
        "Post-Apocalyptic Arcana": [
            "Ash-Home",
            "Rift-Edge",
            "Scrap-Spire",
            "Bone-Hollow",
            "Cinder-Glow",
        ],
        "Gothic Sunless Ocean": [
            "Black-Tide",
            "Drown-Port",
            "Mire-Gallow",
            "Gloom-Bay",
            "Abyssal-Rest",
        ],
        "Shattered Floating Isles": [
            "Sky-Reach",
            "Cloud-Apex",
            "Wind-Grip",
            "Aerie",
            "Zephyr-Rest",
        ],
        "Ancient Sun-Drenched Desert": [
            "Sun-Gate",
            "Oasis-Prime",
            "Silt-Reach",
            "Dune-Wall",
            "Scorpion-Rift",
        ],
        "Solarpunk Arcane Canopy": [
            "Sol-Habitat",
            "Aethel-Flora",
            "Bio-Glass Spire",
            "Verdant Sanctuary",
            "Prism-Glow",
        ],
        "Covenstead & Warlock Pactlands": [
            "Whisper-Hollow",
            "Bramble-Coven",
            "Blackthorn Spire",
            "Eldritch Fen",
            "Moon-Gallows",
        ],
        "Sanguine Aristocracy & Vampire Courts": [
            "Castle Sanguine",
            "Crimson Spire",
            "Blood-Gallow",
            "Scarlet Hold",
            "Vein-Reach",
        ],
        "Silk Route Silk & Spice Merchant Empires": [
            "Jade Haven",
            "Golden Silk Spire",
            "Lotus Port",
            "Spice-Gallow",
            "Emerald Reach",
        ],
    },
    "character_names": {
        "High Fantasy Steampunk": [
            "Gideon Sterling",
            "Vera Gearheart",
            "Silas Vane",
            "Ada Finch",
            "Baron Oswald",
            "Clara Copper",
        ],
        "Post-Apocalyptic Arcana": [
            "Kael Ruin",
            "Marrow",
            "Lyra Dust",
            "Jax Ember",
            "Raven Scraps",
            "Thorne Void",
        ],
        "Gothic Sunless Ocean": [
            "Captain Vane",
            "Corvus Dark",
            "Morwenna Black",
            "Bartholomew Tide",
            "Isolda Deep",
            "Caspian Brine",
        ],
        "Shattered Floating Isles": [
            "Zephyr Vance",
            "Aria Gale",
            "Thorne Skydancer",
            "Skye Storm",
            "Caelum Wing",
            "Lyra Stratus",
        ],
        "Ancient Sun-Drenched Desert": [
            "Tariq Sunstrider",
            "Zahra Silt",
            "Kharon Sand",
            "Samira Sol",
            "Malik Mirage",
            "Azra Dune",
        ],
        "Solarpunk Arcane Canopy": [
            "Zephyr Helios",
            "Flora Glass",
            "Solomon Leaf",
            "Iiris Ray",
            "Kaelen Biomage",
            "Aria Photonic",
        ],
        "Covenstead & Warlock Pactlands": [
            "Morrigan Hex",
            "Malakor Flame",
            "Agatha Thorn",
            "Balthazar Void",
            "Circe Blackwood",
            "Salem Night",
        ],
        "Sanguine Aristocracy & Vampire Courts": [
            "Lord Vladislaus",
            "Lady Carmilla",
            "Count Dragos",
            "Baroness Elizabeth",
            "Lucius Sanguis",
            "Seraphina Crimson",
        ],
        "Silk Route Silk & Spice Merchant Empires": [
            "Zhao Silk-Weaver",
            "Mei-Ling Jade",
            "Kaelen Spice-Lord",
            "Li Wei Gold",
            "Soren Lotus",
            "Chen Emerald",
        ],
    },
    "hooks": [
        "Works as a covert operative for {faction} investigating anomalies near {settlement}.",
        "A former captive of {faction} seeking revenge and answers in {settlement}.",
        "An exiled scholar possessing forbidden knowledge coveted by {faction}.",
        "A local folk hero defending the common people of {settlement} from the influence of {faction}.",
    ],
    "labels": {
        "character_sheet": "D&D CHARACTER SHEET",
        "name": "Name",
        "race": "Race",
        "class": "Class",
        "subclass": "Subclass",
        "level": "Level",
        "background": "Background",
        "faction": "Faction",
        "alignment": "Alignment",
        "identity_overview": "Character Identity & Archetype",
        "attributes": "Attributes & Modifiers",
        "backstory_hook": "Backstory & Campaign Hook",
        "game_universe": "D&D Universe Manual",
        "world_overview": "World Overview & Lore Chronicle",
        "theme": "Theme / Setting",
        "universe_id": "Universe ID",
        "dominant_factions": "Dominant Factions",
        "major_settlements": "Major Settlements",
        "global_conflict": "Main Campaign Story & Regional Crisis",
        "party_members": "Generated Party Adventurers",
        "encounters_title": "Campaign Encounters & Threat Dossier",
        "low_battle": "Stage 1: Introductory Battle",
        "mid_battle": "Stage 2: Escalating Battle",
        "boss_battle": "Stage 3: Climactic Boss Encounter",
        "location": "Battle Location",
        "enemies": "Enemies Encountered",
        "armour": "Armor / Protection",
        "goodies": "Loot & DM Goodies",
        "unlocks": "Story Progression / World Unlock",
        "str": "Strength",
        "dex": "Dexterity",
        "con": "Constitution",
        "int": "Intelligence",
        "wis": "Wisdom",
        "cha": "Charisma",
        "combat_title": "Combat & weaponry statistics",
        "hp": "Health Points (HP)",
        "ac": "Armour Class (AC)",
        "initiative": "Initiative",
        "proficiency": "Proficiency",
        "equipped_armor": "Equipped armor",
        "main_attack": "Main attack",
        "inventory_magic_title": "Inventory and magic",
        "starting_equipment": "Starting equipment",
        "magic_spells": "Magic/spells",
    },
    "theme_encounters": {
        "High Fantasy Steampunk": {
            "low": {
                "location": "Abandoned Gear-Sluice Substation",
                "enemies": [
                    {"name": "Clockwork Scrapper", "type": "Automaton", "armour": "Reinforced Brass Plating (AC 12)", "goodies": "15 gp, Copper Sprocket, Minor Repair Kit"},
                    {"name": "Grease-Monkey Enforcer", "type": "Humanoid", "armour": "Leather Apron & Padded Jacket (AC 11)", "goodies": "Smokepowder Flask, Wrench, 10 gp"}
                ]
            },
            "mid": {
                "location": "Pneumatic Freight Station Alpha",
                "enemies": [
                    {"name": "Steam-Rig Heavy Sentry", "type": "Automaton", "armour": "Riveted Iron Boiler Plate (AC 15)", "goodies": "Ether-Infused Pressure Gauge, 45 gp, Potion of Healing"},
                    {"name": "Aether-Tech Saboteur", "type": "Humanoid", "armour": "Reinforced Flight Leathers (AC 13)", "goodies": "Arc-Welding Torch, Schematic Notes, 30 gp"}
                ]
            },
            "boss": {
                "location": "The Grand Over-Boiler Citadel",
                "enemies": [
                    {"name": "Grand Archon Vane the Steam-Forged", "type": "Clockwork Titan", "armour": "Aether-Shielded Adamantine Armor (AC 18)", "goodies": "Master Ether Regulator Key, 200 gp, Wand of Lightning Bolts"}
                ],
                "unlocks": "Unlocks access to the Sovereign Airship Docks and reveals the blueprint to stabilize the regional ether grid."
            }
        },
        "Post-Apocalyptic Arcana": {
            "low": {
                "location": "Irradiated Ruins Outpost",
                "enemies": [
                    {"name": "Mutated Scavenger", "type": "Mutant", "armour": "Scrap-Metal Hauberk (AC 12)", "goodies": "12 gp, Purified Water Flask, Bone Dagger"},
                    {"name": "Dust-Spitter Hound", "type": "Beast", "armour": "Thick Calcified Hides (AC 11)", "goodies": "Mutated Fang, Sharp Claws"}
                ]
            },
            "mid": {
                "location": "Collapsed Mana Reactor Trench",
                "enemies": [
                    {"name": "Arcane-Warped Marauder", "type": "Mutant", "armour": "Hardened Scrap Armor (AC 14)", "goodies": "Charged Mana Core, 40 gp, Anti-Radiation Salve"},
                    {"name": "Void-Gazer Cultist", "type": "Humanoid", "armour": "Rune-Carved Robes (AC 12)", "goodies": "Scroll of Shatter, Void Essence, 25 gp"}
                ]
            },
            "boss": {
                "location": "The Scorched Void Vault",
                "enemies": [
                    {"name": "Abomination-Lord Malakor", "type": "Arcane Monstrosity", "armour": "Crystalline Chitin Armor (AC 17)", "goodies": "NEXUS Core Crystal, 180 gp, Staff of Fire"}
                ],
                "unlocks": "Restores clean water flow across the wasteland and unlocks the sealed pre-collapse underground bunker."
            }
        },
        "Gothic Sunless Ocean": {
            "low": {
                "location": "Rotting Barnacle Wharf",
                "enemies": [
                    {"name": "Drowned Deckhand", "type": "Undead", "armour": "Tattered Sailor Leathers (AC 11)", "goodies": "10 gp, Waterlogged Journal, Rusty Cutlass"},
                    {"name": "Brine-Cult Initiate", "type": "Humanoid", "armour": "Thick Sea-Kelp Vest (AC 11)", "goodies": "Black Pearl Trinket, Potion of Swimming"}
                ]
            },
            "mid": {
                "location": "Submerged Cathedral Reef",
                "enemies": [
                    {"name": "Abyssal Deep-Diver", "type": "Monstruosidad", "armour": "Heavy Brass Diving Suit (AC 15)", "goodies": "Depth-Pressure Valve, 50 gp, Ring of Water Breathing"},
                    {"name": "Siren Siren-Born Spellweaver", "type": "Monstruosidad", "armour": "Bioluminescent Scale Armor (AC 13)", "goodies": "Charming Sea Shell, 35 gp"}
                ]
            },
            "boss": {
                "location": "The Sunless Trench Sanctum",
                "enemies": [
                    {"name": "Leviathan Priestess Isolda", "type": "Abyssal Noble", "armour": "Coral-Inlaid Plate (AC 17)", "goodies": "Trident of the Deep, 220 gp, Tide-Master's Orb"}
                ],
                "unlocks": "Calms the raging abyssal tides and unveils the submerged coordinates to the Sunken Isle of Kings."
            }
        },
        "Shattered Floating Isles": {
            "low": {
                "location": "Perilous Wind-Bridge Outpost",
                "enemies": [
                    {"name": "Sky-Pirate Corsair", "type": "Humanoid", "armour": "Reinforced Leather Armor (AC 12)", "goodies": "14 gp, Spyglass, Wind-Vane Compass"},
                    {"name": "Gale-Wing Raptor", "type": "Beast", "armour": "Natural Feathered Hide (AC 11)", "goodies": "Razor Quills, Feather Talisman"}
                ]
            },
            "mid": {
                "location": "Shattered Astral Dockyard",
                "enemies": [
                    {"name": "Ether-Sail Captain", "type": "Humanoid", "armour": "Studded Sky-Leather (AC 14)", "goodies": "Gale-Pistol, 55 gp, Potion of Levitation"},
                    {"name": "Zephyr Elemental Construct", "type": "Elemental", "armour": "Swirling Mist Barrier (AC 13)", "goodies": "Essence of Air, Cloud Gem"}
                ]
            },
            "boss": {
                "location": "The Apex Gravity Core Engine",
                "enemies": [
                    {"name": "Sky-Lord Vance the Stormbringer", "type": "Humanoid", "armour": "Aetherium Dragonmail (AC 18)", "goodies": "Aegis Gravity Shard, 250 gp, Boots of Levitation"}
                ],
                "unlocks": "Stabilizes the float-altitude of the archipelagos and opens the ancient portal to the Celestial Heavens."
            }
        },
        "Ancient Sun-Drenched Desert": {
            "low": {
                "location": "Sun-Bleached Dune Oasis",
                "enemies": [
                    {"name": "Sand-Raider Nomad", "type": "Humanoid", "armour": "Desert Padded Wrap (AC 11)", "goodies": "12 gp, Desert Scimitar, Oasis Map"},
                    {"name": "Giant Dune Scorpion", "type": "Beast", "armour": "Chitinous Shell (AC 12)", "goodies": "Venom Sac, Chitin Plate Fragment"}
                ]
            },
            "mid": {
                "location": "Buried Tomb Entrance",
                "enemies": [
                    {"name": "Sun-Cult Zealot", "type": "Humanoid", "armour": "Scale Mail of the Sun (AC 14)", "goodies": "Solar Medallion, 45 gp, Potion of Fire Resistance"},
                    {"name": "Tomb Sentinel Construct", "type": "Construct", "armour": "Carved Sandstone Plate (AC 15)", "goodies": "Gilded Scarab, Gem-encrusted Eye"}
                ]
            },
            "boss": {
                "location": "The Solar Pharaoh's Sanctum",
                "enemies": [
                    {"name": "Pharaoh Kharon the Eternal", "type": "Undead Monarch", "armour": "Golden Solar Plate (AC 18)", "goodies": "Scepter of the Twin Suns, 300 gp, Scarab Amulet of Health"}
                ],
                "unlocks": "Ends the eternal drought by summoning primeval rainfall and unlocks the lost Library of the Sun."
            }
        },
        "Solarpunk Arcane Canopy": {
            "low": {
                "location": "Overgrown Photonic Nursery",
                "enemies": [
                    {"name": "Wild Flora-Drone", "type": "Construct", "armour": "Hardened Wood Shell (AC 12)", "goodies": "10 gp, Bio-Luminescent Bulb, Solar Fiber"},
                    {"name": "Rebel Eco-Poacher", "type": "Humanoid", "armour": "Leaf-Mesh Suit (AC 11)", "goodies": "Entangling Net, 15 gp, Herb Pouch"}
                ]
            },
            "mid": {
                "location": "Bio-Glass Prism Observatory",
                "enemies": [
                    {"name": "Corrupted Photonic Weaver", "type": "Humanoid", "armour": "Prismatic Weave Armor (AC 14)", "goodies": "Light-Focusing Crystal, 50 gp, Potion of Healing"},
                    {"name": "Chitin-Vine Abomination", "type": "Plant", "armour": "Thorny Bark (AC 13)", "goodies": "Rare Seed Pod, Regenerative Sap"}
                ]
            },
            "boss": {
                "location": "The Heart of the Mother Tree",
                "enemies": [
                    {"name": "Arch-Biomancer Helios", "type": "Plant/Humanoid", "armour": "Living Petrified Bark Mail (AC 17)", "goodies": "Prism Seed of Life, 210 gp, Ring of Protection"}
                ],
                "unlocks": "Cleanses the fungal blight affecting the canopy and unlocks the legendary Sun-Canopy Flying Gardens."
            }
        },
        "Covenstead & Warlock Pactlands": {
            "low": {
                "location": "Fog-Shrouded Bramble Hollow",
                "enemies": [
                    {"name": "Bog Hag Acolyte", "type": "Fey", "armour": "Hide of Crows (AC 11)", "goodies": "11 gp, Eye of Newt, Curse Talisman"},
                    {"name": "Imp Familiar", "type": "Fiend", "armour": "Infernal Skin (AC 12)", "goodies": "Fiend Horn, Brimstone Vial"}
                ]
            },
            "mid": {
                "location": "Blackthorn Ritual Circle",
                "enemies": [
                    {"name": "Pact-Bound Warlock", "type": "Humanoid", "armour": "Eldritch Robes (AC 13)", "goodies": "Scroll of Hellish Rebuke, 45 gp, Bloodstone Trinket"},
                    {"name": "Bramble Shadow-Beast", "type": "Monstrosity", "armour": "Entangled Thorn Armor (AC 14)", "goodies": "Thorn Heart, Shadow Essence"}
                ]
            },
            "boss": {
                "location": "The Blood-Moon Covenstead Altar",
                "enemies": [
                    {"name": "Matriarch Morrigan the Hex-Weaver", "type": "Fey/Humanoid", "armour": "Shadow-Pact Cuirass (AC 17)", "goodies": "Grimoire of the Primordial Pact, 240 gp, Rod of the Pact Keeper"}
                ],
                "unlocks": "Binds the dark fiendish rifts across the realm and grants the party passage into the Nether Realm."
            }
        },
        "Sanguine Aristocracy & Vampire Courts": {
            "low": {
                "location": "Cobblestone Crypt Entrance",
                "enemies": [
                    {"name": "Rival Blood-Thrall Guard", "type": "Humanoid", "armour": "Padded Velvet Livery (AC 11)", "goodies": "15 gp, Silver Coin, Steel Dagger"},
                    {"name": "Feral Vampire Bat Swarm", "type": "Beast", "armour": "Evasive Agility (AC 12)", "goodies": "Vampiric Fang, Bat Wing"}
                ]
            },
            "mid": {
                "location": "Scarlet Hold Ballroom",
                "enemies": [
                    {"name": "Rival Clan Vampire Fencer", "type": "Undead", "armour": "Fine Studded Silk (AC 14)", "goodies": "Masterwork Rapier, 60 gp, Blood-Ruby Ring"},
                    {"name": "Sanguine Blood-Mage", "type": "Undead", "armour": "Crimson Court Robes (AC 13)", "goodies": "Vial of Pure Blood, Scroll of Vampiric Touch"}
                ]
            },
            "boss": {
                "location": "The Grand Crimson Crypt Spire",
                "enemies": [
                    {"name": "Count Vladislaus the Blood Sovereign", "type": "Vampire Lord", "armour": "Sanguine Plate of the Night (AC 18)", "goodies": "Signet Ring of the High Court, 350 gp, Cloak of the Bat"}
                ],
                "unlocks": "Abolishes the aristocratic blood tax and grants control over Castle Sanguine and its hidden vaults."
            }
        },
        "Silk Route Silk & Spice Merchant Empires": {
            "low": {
                "location": "Ambushed Spice Route Oasis",
                "enemies": [
                    {"name": "Caravan Bandit", "type": "Humanoid", "armour": "Light Padded Silk (AC 11)", "goodies": "18 gp, Bag of Exotic Cinnamon, Scimitar"},
                    {"name": "Trained Attack Falcon", "type": "Beast", "armour": "Swift Flight (AC 12)", "goodies": "Feather Whistle"}
                ]
            },
            "mid": {
                "location": "Fortified Silk Warehouse",
                "enemies": [
                    {"name": "Mercenary Guild Enforcer", "type": "Humanoid", "armour": "Jade-Studded Scale Armor (AC 14)", "goodies": "Guild Pass, 50 gp, Smoke Bomb"},
                    {"name": "Alchemical Spice-Thrower", "type": "Humanoid", "armour": "Reinforced Leather (AC 13)", "goodies": "3x Potion of Blinding Spice, 40 gp"}
                ]
            },
            "boss": {
                "location": "The Golden Lotus Pagoda Fortress",
                "enemies": [
                    {"name": "Spice-Lord Zhao the Golden", "type": "Humanoid Mastermind", "armour": "Imperial Dragon-Silk Scale Mail (AC 17)", "goodies": "Imperial Seal of Trade, 400 gp, Golden Dragon Blade"}
                ],
                "unlocks": "Unlocks the exclusive Silk Route Merchant Charter, granting unlimited trade concessions across all empires."
            }
        }
    }
}

DATA_ES = {
    "themes": {
        "1": "Alta Fantasía Steampunk",
        "2": "Arcana Post-Apocalíptica",
        "3": "Océano Gótico Sin Sol",
        "4": "Islas Flotantes Fragmentadas",
        "5": "Desierto Ancestral Abrasador",
        "6": "Canopia Arcana Solarpunk",
        "7": "Aquelarre y Tierras de Pacto de Brujos",
        "8": "Aristocracia Sanguínea y Cortes Vampíricas",
        "9": "Imperios Mercantiles de la Ruta de la Seda y Especias",
    },
    "faction_types": [
        "Gremio",
        "Culto",
        "Imperio",
        "Sindicato Rebelde",
        "Círculo Druídico",
        "Alianza de Eco-Ingenieros",
    ],
    "faction_adjectives_1": [
        "de Hierro",
        "Dorado",
        "Sombreado",
        "Arcano",
        "Celestial",
        "Frondoso",
    ],
    "faction_adjectives_2": [
        "Carmesí",
        "Silencioso",
        "Sin Límites",
        "Verdoso",
        "Ébano",
        "Solar",
    ],
    "alignments": [
        "Legal Bueno", "Neutral Bueno", "Caótico Bueno",
        "Legal Neutral", "Neutral Puro", "Caótico Neutral",
        "Legal Malvado", "Neutral Malvado", "Caótico Malvado"
    ],
    "alignment_descriptions": {
        "Legal Bueno": "Combina honor y compasión, actuando conforme a las normas e integridad moral para proteger a los demás.",
        "Neutral Bueno": "Guiado por su conciencia para hacer lo correcto, ayudando al prójimo sin importar leyes o autoridad.",
        "Caótico Bueno": "Sigue su brújula moral hacia la libertad y la bondad, rebelándose activamente contra la tiranía.",
        "Legal Neutral": "Actúa guiado por la ley, el orden o un código personal estricto sin inclinarse hacia el bien o el mal.",
        "Neutral Puro": "Prefiere el equilibrio moral y evita comprometerse ciegamente con ideologías extremas.",
        "Caótico Neutral": "Valora su libertad personal por encima de todo, siguiendo impulsos sin malicia ni altruismo.",
        "Legal Malvado": "Usa metódicamente el orden, las leyes o la autoridad para manipular el sistema en su propio beneficio.",
        "Neutral Malvado": "Puramente egoísta, hace lo necesario para obtener poder sin importar el honor o el caos innecesario.",
        "Caótico Malvado": "Motivado por impulsos destructivos y deseos egoístas, sin respeto por la vida, las normas o el orden."
    },
    "races": [
        "Humano",
        "Elfo",
        "Enano",
        "Mediano",
        "Tiefling",
        "Dracónido",
        "Gnomo",
        "Semi-Orco",
    ],
    "classes": [
        "Guerrero",
        "Mago",
        "Pícaro",
        "Clérigo",
        "Explorador",
        "Paladín",
        "Bardo",
        "Druida",
        "Brujo",
    ],
    "subclasses": {
        "Guerrero": ["Campeón", "Maestro del Combate", "Caballero Arcano"],
        "Mago": ["Escuela de Evocación", "Escuela de Abjuración", "Escuela de Adivinación"],
        "Pícaro": ["Ladrón", "Asesino", "Embaucador Arcano"],
        "Clérigo": ["Dominio de la Vida", "Dominio de la Luz", "Dominio de la Guerra"],
        "Explorador": ["Cazador", "Maestro de Bestias", "Cazador de Sombras"],
        "Paladín": ["Juramento de Devoción", "Juramento de los Antiguos", "Juramento de Venganza"],
        "Bardo": ["Colegio del Conocimiento", "Colegio del Valor", "Colegio del Glamour"],
        "Druida": ["Círculo de la Tierra", "Círculo de la Luna", "Círculo de las Estrellas"],
        "Brujo": ["El Primordial", "El Gran Antiguo", "El Archifeérico"],
    },
    "subclass_descriptions": {
        "Campeón": "Se enfoca en la fuerza física pura, perfeccionando sus ataques para asestar golpes críticos devastadores.",
        "Maestro del Combate": "Emplea maniobras tácticas y dados de superioridad para dominar tácticamente el campo de batalla.",
        "Caballero Arcano": "Combina la destreza marcial con magia de abjuración y evocación para una gran versatilidad.",
        "Escuela de Evocación": "Maestro de las fuerzas elementales, moldea potentes conjuros destructivos protegiendo a sus aliados.",
        "Escuela de Abjuración": "Especializado en barreras protectoras, contrahechizos y magia defensiva de contención.",
        "Escuela de Adivinación": "Atisba el futuro para alterar el destino, previendo los resultados antes de que sucedan.",
        "Ladrón": "Mejora la agilidad y el sigilo, forzando cerraduras y usando objetos rápidamente en pleno combate.",
        "Asesino": "Maestro del ataque sorpresa, el disfraz y mortales venenos infligidos desde las sombras.",
        "Embaucador Arcano": "Potencia el sigilo del pícaro mediante hechizos de ilusión y encantamiento para confundir al rival.",
        "Dominio de la Vida": "Canalizador de energía divina centrado en restaurar la salud y preservar la vida de sus aliados.",
        "Dominio de la Luz": "Maneja el fuego divino y una luz radiante e cegadora para abrasar a las criaturas de la oscuridad.",
        "Dominio de la Guerra": "Un guerrero santo que inspira la excelencia marcial y otorga ataques guiados por su fe.",
        "Cazador": "Especializado en combatir contra hordas de enemigos o bestias gigantes mediante técnicas avanzadas.",
        "Maestro de Bestias": "Forja un vínculo profundo con un compañero animal salvaje que lucha lealmente a su lado.",
        "Cazador de Sombras": "Un emboscador de tierras salvajes que domina la oscuridad profunda y las cavernas subterráneas.",
        "Juramento de Devoción": "Encarna el ideal del caballero de brillante armadura, guiado firmemente por el honor y la justicia.",
        "Juramento de los Antiguos": "Lucha por la luz y la naturaleza, preservando la vida, la belleza y la vegetación ancestral.",
        "Juramento de Venganza": "Un castigador implacable que persigue a los malhechores para impartir retribución estricta.",
        "Colegio del Conocimiento": "Reúne saberes y secretos de múltiples campos, tejiendo palabras cortantes y conjuros extra.",
        "Colegio del Valor": "Entona épicas sagas para inspirar a sus aliados en combate marcial mientras viste armadura pesada.",
        "Colegio del Glamour": "Canaliza magia feérica para cautivar audiencias y exigir respeto con una gracia deslumbrante.",
        "Círculo de la Tierra": "Preserva tradiciones místicas antiguas y extrae poder directamente de diversos terrenos salvajes.",
        "Círculo de la Luna": "Maestro de la forma salvaje, transformándose en poderosas bestias elementales durante el combate.",
        "Círculo de las Estrellas": "Aprovecha las constelaciones celestiales para canalizar luz radiante y presagios cósmicos.",
        "El Primordial": "Vinculado a un demonio o diablo de los planos inferiores, obteniendo magia de fuego y vitalidad oscura.",
        "El Gran Antiguo": "Obtiene poderes mentales alienígenas e inquietantes de entidades cósmicas más allá de las estrellas.",
        "El Archifeérico": "Maneja magia feérica caprichosa y engañosa para fascinar, aterrorizar y teleportarse con soltura.",
    },
    "skills_by_attr": {
        "STR": ["Atletismo"],
        "DEX": ["Acrobacias", "Juego de Manos", "Sigilo"],
        "CON": [],
        "INT": ["Arcano", "Historia", "Investigación", "Naturaleza", "Religión"],
        "WIS": ["Trato con Animales", "Perspicacia", "Medicina", "Percepción", "Supervivencia"],
        "CHA": ["Engaño", "Intimidación", "Interpretación", "Persuasión"]
    },
    "backgrounds": [
        "Acólito",
        "Criminal",
        "Héroe del Pueblo",
        "Noble",
        "Sabio",
        "Soldado",
        "Gamberro",
        "Forastero",
    ],
    "race_descriptions": {
        "Humano": "Versátiles y ambiciosos, los humanos son supervivientes adaptables que prosperan en casi cualquier entorno.",
        "Elfo": "Seres mágicos y longevos con una profunda conexión con la naturaleza, la gracia y la sabiduría ancestral.",
        "Enano": "Guerreros y artesanos tenaces, resistentes y audaces, forjados en los profundos salones de las montañas.",
        "Mediano": "Un pueblo pequeño y alegre cuya sorprendente suerte y sigilo a menudo superan su modesto tamaño.",
        "Tiefling": "De linaje infernal, los tieflings navegan el mundo con una determinación ardiente y carisma magnético.",
        "Dracónido": "Orgullosos descendientes de dragones que honran su linaje con fuerza e infligen aliento elemental.",
        "Gnomo": "Inventores e ingeniosos bromistas llenos de energía y curiosidad desbordante por el mundo.",
        "Semi-Orco": "Luchadores feroces poseedores de una tenacidad e imparable fuerza física e indomable.",
    },
    "class_descriptions": {
        "Guerrero": "Un maestro del combate marcial, experto en el uso de diversa variedad de armas y armaduras.",
        "Mago": "Un estudioso de la magia capaz de alterar la estructura de la realidad mediante conjuros arcanos.",
        "Pícaro": "Un rufián que utiliza el sigilo, la precisión y la agilidad para explotar las debilidades del enemigo.",
        "Clérigo": "Un campeón sacerdotal que canaliza magia divina al servicio de una entidad superior o deidad.",
        "Explorador": "Un cazador de la naturaleza, experto en rastrear enemigos y dominar técnicas de supervivencia.",
        "Paladín": "Un guerrero santo vinculado a un juramento sagrado, combinando magia divina y pesada armadura.",
        "Bardo": "Un artista inspirador cuya música y palabras moldean sutiles hilos de poder mágico.",
        "Druida": "Un sacerdote de la Antigua Fe que canaliza las fuerzas primigenias de la naturaleza y formas animales.",
        "Brujo": "Un buscador de conocimientos esotéricos que ha forjado un pacto con una entidad de otro mundo.",
    },
    "background_descriptions": {
        "Acólito": "Dedicó años al servicio en un templo, actuando como intermediario entre la vida mortal y lo divino.",
        "Criminal": "Un delincuente experimentado con un amplio historial de tratos ilícitos y contactos en el inframundo.",
        "Héroe del Pueblo": "Un campeón de las clases humildes cuya valentía se alza frente a la opresión y el peligro.",
        "Noble": "Nacido en la riqueza y el privilegio, acostumbrado al poder, la influencia y las altas expectativas sociales.",
        "Sabio": "Un erudito dedicado que pasó años acumulando sabiduría, investigaciones y textos antiguos.",
        "Soldado": "Entrenado en la guerra táctica, la disciplina militar y la dura vida del combate en el campo de batalla.",
        "Gamberro": "Creció en la pobreza y la calle, dependiendo de su astucia e instintos urbanos para sobrevivir.",
        "Forastero": "Criado en tierras salvajes lejos de la civilización, experto en rastreo, naturaleza y supervivencia.",
    },
    "settlements": {
        "Alta Fantasía Steampunk": [
            "Engranajeburgo",
            "CrestadeLatón",
            "EspiraAérea",
            "PuertoHierro",
            "VaporGallow",
        ],
        "Arcana Post-Apocalíptica": [
            "HogarCeniza",
            "BordeGrieta",
            "ChatarraEspira",
            "HuesoVacío",
            "ResplandorCeniza",
        ],
        "Océano Gótico Sin Sol": [
            "MareaNegra",
            "PuertoAhogado",
            "FangoAhorcado",
            "BahíaPenumbra",
            "ReposAbisal",
        ],
        "Islas Flotantes Fragmentadas": [
            "CumbreCielo",
            "ÁpexNube",
            "GarraViento",
            "NidoÁguila",
            "ReposCéfiro",
        ],
        "Desierto Ancestral Abrasador": [
            "PuertaSol",
            "OasisPrima",
            "AlcanceLimo",
            "MuroDuna",
            "GrietaEscorpión",
        ],
        "Canopia Arcana Solarpunk": [
            "Sol-Hábitat",
            "Aethel-Flora",
            "Espira de Bio-Cristal",
            "Santuario Frondoso",
            "Destello Prismático",
        ],
        "Aquelarre y Tierras de Pacto de Brujos": [
            "Susurro-Hueco",
            "Aquelarre-Maleza",
            "Espira del Espino Negro",
            "Pantanales Eldritch",
            "Horca de la Luna",
        ],
        "Aristocracia Sanguínea y Cortes Vampíricas": [
            "Castillo Sanguíneo",
            "Espira Carmesí",
            "Horca de Sangre",
            "Bastión Escarlata",
            "Alcance de la Vena",
        ],
        "Imperios Mercantiles de la Ruta de la Seda y Especias": [
            "Refugio de Jade",
            "Espira de Seda Dorada",
            "Puerto del Loto",
            "Horca de las Especias",
            "Alcance Esmeralda",
        ],
    },
    "character_names": {
        "Alta Fantasía Steampunk": [
            "Gedeón Sterling",
            "Vera Ensamble",
            "Silas Vane",
            "Ada Finch",
            "Barón Osvaldo",
            "Clara Cobre",
        ],
        "Arcana Post-Apocalíptica": [
            "Kael Ruina",
            "Tuétano",
            "Lyra Polvo",
            "Jax Ascua",
            "Cuervo Chatarra",
            "Espina Vacío",
        ],
        "Océano Gótico Sin Sol": [
            "Capitán Vane",
            "Corvus Oscuro",
            "Morwenna Negra",
            "Bartolomé Marea",
            "Isolda Profunda",
            "Caspio Salmuera",
        ],
        "Islas Flotantes Fragmentadas": [
            "Céfiro Vance",
            "Aria Galerna",
            "Espina Danzacielos",
            "Skye Tormenta",
            "Caelum Ala",
            "Lyra Estrato",
        ],
        "Desierto Ancestral Abrasador": [
            "Tariq Caminasol",
            "Zahra Limo",
            "Caronte Arena",
            "Samira Sol",
            "Malik Espejismo",
            "Azra Duna",
        ],
        "Canopia Arcana Solarpunk": [
            "Céfiro Helios",
            "Flora Cristal",
            "Salomón Hoja",
            "Iiris Rayo",
            "Kaelen Biomage",
            "Aria Fotónica",
        ],
        "Aquelarre y Tierras de Pacto de Brujos": [
            "Morrigan Hex",
            "Malakor Llama",
            "Agatha Espino",
            "Baltazar Vacío",
            "Circe Bosquenegro",
            "Salem Noche",
        ],
        "Aristocracia Sanguínea y Cortes Vampíricas": [
            "Lord Vladislaus",
            "Lady Carmilla",
            "Conde Dragos",
            "Baronesa Elizabeth",
            "Lucius Sanguis",
            "Seraphina Carmesí",
        ],
        "Imperios Mercantiles de la Ruta de la Seda y Especias": [
            "Zhao Tejedor de Seda",
            "Mei-Ling Jade",
            "Kaelen Señor de la Especia",
            "Li Wei Oro",
            "Soren Loto",
            "Chen Esmeralda",
        ],
    },
    "hooks": [
        "Trabaja como agente encubierto para {faction} investigando anomalías cerca de {settlement}.",
        "Un antiguo cautivo de {faction} que busca venganza y respuestas en {settlement}.",
        "Un erudito exiliado que posee conocimientos prohibidos codiciados por {faction}.",
        "Un héroe local que defiende al pueblo llano de {settlement} frente a la influencia de {faction}.",
    ],
    "labels": {
        "character_sheet": "",
        "name": "Nombre",
        "race": "Raza",
        "class": "Clase",
        "subclass": "Subclase",
        "level": "Nivel",
        "background": "Trasfondo",
        "faction": "Facción",
        "alignment": "Alineación",
        "identity_overview": "Identidad del Personaje y Arquetipo",
        "attributes": "Atributos y Modificadores",
        "backstory_hook": "Historia y Gancho de Campaña",
        "game_universe": "Manual del Universo D&D",
        "world_overview": "Resumen del Mundo y Crónica Histórica",
        "theme": "Tema / Ambientación",
        "universe_id": "ID del Universo",
        "dominant_factions": "Facciones Dominantes",
        "major_settlements": "Asentamientos Principales",
        "global_conflict": "Trama Principal y Conflicto Regional",
        "party_members": "Aventureros del Grupo Generados",
        "encounters_title": "Dossier de Encuentros y Amenazas",
        "low_battle": "Fase 1: Batalla Introductoria de Nivel Bajo",
        "mid_battle": "Fase 2: Batalla Intermedia Escalada",
        "boss_battle": "Fase 3: Enfrentamiento Épico contra el Jefe Final",
        "location": "Lugar del Combate",
        "enemies": "Enemigos Presentes",
        "armour": "Armadura / Protección BÁSICA",
        "goodies": "Botín y Recompensas para el DM",
        "unlocks": "Desbloqueo de Trama / Avance de la Historia",
        "str": "Fuerza",
        "dex": "Destreza",
        "con": "Constitución",
        "int": "Inteligencia",
        "wis": "Sabiduría",
        "cha": "Carisma",
        "combat_title": "Estadísticas de combate y armamento",
        "hp": "Puntos de Golpe (PV)",
        "ac": "Clase de Armadura (CA)",
        "initiative": "Iniciativa",
        "proficiency": "Competencia",
        "equipped_armor": "Armadura equipada",
        "main_attack": "Ataque principal",
        "inventory_magic_title": "Inventario y magia",
        "starting_equipment": "Equipo inicial",
        "magic_spells": "Magia/conjuros",
    },
    "theme_encounters": {
        "Alta Fantasía Steampunk": {
            "low": {
                "location": "Subestación de Compuertas de Engranajes Abandonada",
                "enemies": [
                    {"name": "Chatarrero de Relojería", "type": "Autómata", "armour": "Placas de Latón Reforzado (CA 12)", "goodies": "15 po, Engranaje de Cobre, Kit de Reparación Menor"},
                    {"name": "Matón Engrasador", "type": "Humanoide", "armour": "Delantal de Cuero y Chaqueta Acolchada (CA 11)", "goodies": "Frasco de Pólvora de Humo, Llave Inglesa, 10 po"}
                ]
            },
            "mid": {
                "location": "Estación de Carga Neumática Alfa",
                "enemies": [
                    {"name": "Centinela Pesado a Vapor", "type": "Autómata", "armour": "Placa de Caldera de Hierro Remachado (CA 15)", "goodies": "Manómetro de Presión Infundido en Éter, 45 po, Poción de Curación"},
                    {"name": "Saboteador de Tecnología Éter", "type": "Humanoide", "armour": "Cuero de Vuelo Reforzado (CA 13)", "goodies": "Soplete de Arco Voltaico, Notas de Esquemas, 30 po"}
                ]
            },
            "boss": {
                "location": "La Ciudadela de la Gran Caldera Maestra",
                "enemies": [
                    {"name": "Gran Arconte Vane el Forjado en Vapor", "type": "Titán Mecánico", "armour": "Armadura de Adamantina con Escudo de Éter (CA 18)", "goodies": "Llave Reguladora Maestra de Éter, 200 po, Varita de Rayos Relámpago"}
                ],
                "unlocks": "Desbloquea el acceso a los Muelles del Aerostato Soberano y revela el plano para estabilizar la red de éter regional."
            }
        },
        "Arcana Post-Apocalíptica": {
            "low": {
                "location": "Puesto Avanzado en Ruinas Irradiadas",
                "enemies": [
                    {"name": "Carroñero Mutado", "type": "Mutante", "armour": "Cota de Chatarra Metálica (CA 12)", "goodies": "12 po, Frasco de Agua Purificada, Daga de Hueso"},
                    {"name": "Sabueso Escupe-Polvo", "type": "Bestia", "armour": "Pieles Calcificadas Gruesas (CA 11)", "goodies": "Colmillo Mutado, Garras Afiladas"}
                ]
            },
            "mid": {
                "location": "Trinchera del Reactor de Maná Colapsado",
                "enemies": [
                    {"name": "Merodeador Deformado por la Magia", "type": "Mutante", "armour": "Armadura de Chatarra Endurecida (CA 14)", "goodies": "Núcleo de Maná Cargado, 40 po, Ungüento Anti-Radiación"},
                    {"name": "Cultista del Vacío", "type": "Humanoide", "armour": "Túnicas Grabadas con Runas (CA 12)", "goodies": "Pergamino de Estallar, Esencia del Vacío, 25 po"}
                ]
            },
            "boss": {
                "location": "La Bóveda Abrasada del Vacío",
                "enemies": [
                    {"name": "Señor Abominación Malakor", "type": "Monstruosidad Arcana", "armour": "Armadura de Quitina Cristalina (CA 17)", "goodies": "Cristal Núcleo NEXUS, 180 po, Bastón de Fuego"}
                ],
                "unlocks": "Restaura el flujo de agua limpia en el páramo y desbloquea el búnker subterráneo sellado antes del colapso."
            }
        },
        "Océano Gótico Sin Sol": {
            "low": {
                "location": "Muelle de Escaramujos Podridos",
                "enemies": [
                    {"name": "Marinero Ahogado", "type": "No-Muerto", "armour": "Cueros Harapientos de Marinero (CA 11)", "goodies": "10 po, Diario Empapado, Alfanje Oxidado"},
                    {"name": "Iniciado del Culto de la Salmuera", "type": "Humanoide", "armour": "Chaleco de Algas Marinas Gruesas (CA 11)", "goodies": "Abalorio de Perla Negra, Poción de Natación"}
                ]
            },
            "mid": {
                "location": "Arrecife de la Catedral Sumergida",
                "enemies": [
                    {"name": "Buzo de las Profundidades Abisales", "type": "Monstruosidad", "armour": "Traje Pesado de Buceo de Latón (CA 15)", "goodies": "Válvula de Presión Profunda, 50 po, Anillo de Respiración Acuática"},
                    {"name": "Tejedor de Conjuros Sireno", "type": "Monstruosidad", "armour": "Armadura de Escamas Bioluminiscentes (CA 13)", "goodies": "Concha Cautivadora, 35 po"}
                ]
            },
            "boss": {
                "location": "El Santuario de la Fosa Sin Sol",
                "enemies": [
                    {"name": "Sacerdotisa Leviatán Isolda", "type": "Noble Abisal", "armour": "Placa de Coral Incrustado (CA 17)", "goodies": "Tridente de las Profundidades, 220 po, Orbe del Maestro de Mares"}
                ],
                "unlocks": "Calma las furiosas mareas abisales y revela las coordenadas sumergidas de la Isla Hundida de los Reyes."
            }
        },
        "Islas Flotantes Fragmentadas": {
            "low": {
                "location": "Puesto Avanzado del Puente de Viento Peligroso",
                "enemies": [
                    {"name": "Corsario Pirata del Cielo", "type": "Humanoide", "armour": "Armadura de Cuero Reforzado (CA 12)", "goodies": "14 po, Catalejo, Brújula de Viento"},
                    {"name": "Raptor del Vendaval", "type": "Bestia", "armour": "Piel Plumosa Natural (CA 11)", "goodies": "Plumas Afiladas, Talismán de Plumas"}
                ]
            },
            "mid": {
                "location": "Astillero Astral Fragmentado",
                "enemies": [
                    {"name": "Capitán Navegante de Éter", "type": "Humanoide", "armour": "Cuero Celeste Tachonado (CA 14)", "goodies": "Pistola de Galerna, 55 po, Poción de Levitación"},
                    {"name": "Constructo Elemental de Céfiro", "type": "Elemental", "armour": "Barrera de Niebla Arremolinada (CA 13)", "goodies": "Esencia de Aire, Gema de Nube"}
                ]
            },
            "boss": {
                "location": "El Motor del Núcleo Gravitacional Ápex",
                "enemies": [
                    {"name": "Señor del Cielo Vance el Traedor de Tormentas", "type": "Humanoide", "armour": "Malla de Dragón de Aetherium (CA 18)", "goodies": "Fragmento de Gravidez Égida, 250 po, Botas de Levitación"}
                ],
                "unlocks": "Estabiliza la altitud de flotación de los archipiélagos y abre el portal antiguo hacia los Cielos Celestiales."
            }
        },
        "Desierto Ancestral Abrasador": {
            "low": {
                "location": "Oasis de Dunas Blanqueadas por el Sol",
                "enemies": [
                    {"name": "Nómada Incursor de la Arena", "type": "Humanoide", "armour": "Túnica Acolchada del Desierto (CA 11)", "goodies": "12 po, Cimitarra del Desierto, Mapa del Oasis"},
                    {"name": "Escorpión Gigante de las Dunas", "type": "Bestia", "armour": "Caparazón Quitinoso (CA 12)", "goodies": "Saco de Veneno, Fragmento de Placa Quitinosa"}
                ]
            },
            "mid": {
                "location": "Entrada a la Tumba Sepultada",
                "enemies": [
                    {"name": "Fanático del Culto Solar", "type": "Humanoide", "armour": "Cota de Escamas del Sol (CA 14)", "goodies": "Medallón Solar, 45 po, Poción de Resistencia al Fuego"},
                    {"name": "Centinela de Piedra de la Tumba", "type": "Constructo", "armour": "Placa de Arenisca Tallada (CA 15)", "goodies": "Escarabajo Dorado, Ojo Incrustado de Gemas"}
                ]
            },
            "boss": {
                "location": "El Santuario del Faraón Solar",
                "enemies": [
                    {"name": "Faraón Caronte el Eterno", "type": "Monarca No-Muerto", "armour": "Placa Solar Dorada (CA 18)", "goodies": "Cetro de los Soles Gemelos, 300 po, Abalorio de Escarabajo de Salud"}
                ],
                "unlocks": "Pone fin a la sequía eterna invocando lluvias primigenias y desbloquea la Biblioteca Perdida del Sol."
            }
        },
        "Canopia Arcana Solarpunk": {
            "low": {
                "location": "Vivero Fotónico Asilvestrado",
                "enemies": [
                    {"name": "Dron Flora Silvestre", "type": "Constructo", "armour": "Caparazón de Madera Endurecida (CA 12)", "goodies": "10 po, Bulbo Bioluminiscente, Fibra Solar"},
                    {"name": "Furtivo Eco-Rebelde", "type": "Humanoide", "armour": "Traje de Malla de Hojas (CA 11)", "goodies": "Red Atrapadora, 15 po, Bolsa de Hierbas"}
                ]
            },
            "mid": {
                "location": "Observatorio de Prismas de Bio-Cristal",
                "enemies": [
                    {"name": "Tejedor Fotónico Corrupto", "type": "Humanoide", "armour": "Armadura de Tejido Prismático (CA 14)", "goodies": "Cristal de Enfoque de Luz, 50 po, Poción de Curación"},
                    {"name": "Abominación de Enredaderas Quitinosas", "type": "Planta", "armour": "Corteza de Espinas (CA 13)", "goodies": "Vaina de Semilla Rara, Savia Regenerativa"}
                ]
            },
            "boss": {
                "location": "El Corazón del Árbol Madre",
                "enemies": [
                    {"name": "Arqui-Biomante Helios", "type": "Planta/Humanoide", "armour": "Malla de Corteza Petrificada Viva (CA 17)", "goodies": "Semilla Prisma de Vida, 210 po, Anillo de Protección"}
                ],
                "unlocks": "Limpia la plaga de hongos que afecta a la canopia y desbloquea los legendarios Jardines Flotantes del Sol."
            }
        },
        "Aquelarre y Tierras de Pacto de Brujos": {
            "low": {
                "location": "Hueco de Maleza Cubierto de Niebla",
                "enemies": [
                    {"name": "Acólita de la Bruja del Pantano", "type": "Feérico", "armour": "Piel de Cuervos (CA 11)", "goodies": "11 po, Ojo de Tritón, Talismán de Maldición"},
                    {"name": "Familiar Duendecillo", "type": "Demonio", "armour": "Piel Infernal (CA 12)", "goodies": "Cuerno Infernal, Frasco de Azufre"}
                ]
            },
            "mid": {
                "location": "Círculo Ritual del Espino Negro",
                "enemies": [
                    {"name": "Brujo Vinculado por Pacto", "type": "Humanoide", "armour": "Túnicas Eldritch (CA 13)", "goodies": "Pergamino de Reprensión Hellish, 45 po, Abalorio de Piedra de Sangre"},
                    {"name": "Bestia Sombreada de Espinos", "type": "Monstruosidad", "armour": "Armadura de Espinas Enredadas (CA 14)", "goodies": "Corazón de Espino, Esencia de Sombra"}
                ]
            },
            "boss": {
                "location": "El Altar del Aquelarre de la Luna de Sangre",
                "enemies": [
                    {"name": "Matriarca Morrigan la Tejedora de Maleficios", "type": "Feérico/Humanoide", "armour": "Coraza de Pacto Sombreado (CA 17)", "goodies": "Grimorio del Pacto Primordial, 240 po, Bastón del Guardián del Pacto"}
                ],
                "unlocks": "Sella las rifts demoníacas oscuras en todo el reino y otorga al grupo el paso hacia el Reino Infernal."
            }
        },
        "Aristocracia Sanguínea y Cortes Vampíricas": {
            "low": {
                "location": "Entrada a las Criptas de Adoquines",
                "enemies": [
                    {"name": "Guardia Siervo de Sangre Rival", "type": "Humanoide", "armour": "Livrea de Terciopelo Acolchado (CA 11)", "goodies": "15 po, Moneda de Plata, Daga de Acero"},
                    {"name": "Enjambre de Murciélagos Vampíricos Ferales", "type": "Bestia", "armour": "Agilidad Evasiva (CA 12)", "goodies": "Colmillo Vampírico, Ala de Murciélago"}
                ]
            },
            "mid": {
                "location": "Salón de Baile del Bastión Escarlata",
                "enemies": [
                    {"name": "Esgrimista Vampiro del Clan Rival", "type": "No-Muerto", "armour": "Seda Tachonada Fina (CA 14)", "goodies": "Roper Maestra, 60 po, Anillo con Rubí de Sangre"},
                    {"name": "Mago de Sangre Sanguíneo", "type": "No-Muerto", "armour": "Túnicas de la Corte Carmesí (CA 13)", "goodies": "Vial de Sangre Pura, Pergamino de Toque Vampírico"}
                ]
            },
            "boss": {
                "location": "La Espira de la Gran Cripta Carmesí",
                "enemies": [
                    {"name": "Conde Vladislaus el Soberano de Sangre", "type": "Señor Vampiro", "armour": "Placa Sanguínea de la Noche (CA 18)", "goodies": "Anillo del Sello de la Alta Corte, 350 po, Capa del Murciélago"}
                ],
                "unlocks": "Abole el impuesto de sangre aristocrático y otorga el control absoluto sobre el Castillo Sanguíneo y sus bóvedas."
            }
        },
        "Imperios Mercantiles de la Ruta de la Seda y Especias": {
            "low": {
                "location": "Oasis de la Ruta de las Especias Emboscado",
                "enemies": [
                    {"name": "Bandido de Caravanas", "type": "Humanoide", "armour": "Seda Acolchada Ligera (CA 11)", "goodies": "18 po, Bolsa de Canela Exótica, Cimitarra"},
                    {"name": "Halcón de Ataque Entrenado", "type": "Bestia", "armour": "Vuelo Rápido (CA 12)", "goodies": "Silbato de Plumas"}
                ]
            },
            "mid": {
                "location": "Almacén Fortificado de Seda",
                "enemies": [
                    {"name": "Matón del Gremio de Mercenarios", "type": "Humanoide", "armour": "Armadura de Escamas Tachonada de Jade (CA 14)", "goodies": "Pase del Gremio, 50 po, Bomba de Humo"},
                    {"name": "Lanzador de Especias Alquímicas", "type": "Humanoide", "armour": "Cuero Reforzado (CA 13)", "goodies": "3x Poción de Especia Cegadora, 40 po"}
                ]
            },
            "boss": {
                "location": "Fortaleza Pagoda del Loto Dorado",
                "enemies": [
                    {"name": "Señor de la Especia Zhao el Dorado", "type": "Mente Maestra Humanoide", "armour": "Cota de Escamas de Seda de Dragón Imperial (CA 17)", "goodies": "Sello Imperial de Comercio, 400 po, Espada del Dragón Dorado"}
                ],
                "unlocks": "Desbloquea la Cédula Mercantil Exclusiva de la Ruta de la Seda, otorgando concesiones comerciales ilimitadas en todos los imperios."
            }
        }
    }
}

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def get_next_game_folder(base_path: str = ".") -> str:
    """Finds the next iterative folder name gameN (game1, game2, etc.)."""
    n = 1
    while True:
        folder_name = f"game{n}"
        full_path = os.path.join(base_path, folder_name)
        if not os.path.exists(full_path):
            return full_path
        n += 1

def roll_stat() -> int:
    rolls = [random.randint(1, 6) for _ in range(4)]
    rolls.remove(min(rolls))
    return sum(rolls)

def calc_modifier(score: int) -> str:
    mod = (score - 10) // 2
    return f"+{mod}" if mod >= 0 else str(mod)

def generate_stats() -> Dict[str, Dict[str, Any]]:
    stats_keys = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    stats = {}
    for key in stats_keys:
        val = roll_stat()
        stats[key] = {"score": val, "mod": calc_modifier(val)}
    return stats

# ==========================================
# ENEMY & ENCOUNTER GENERATOR
# ==========================================

def generate_encounters(chosen_theme_name: str, lang_data: dict) -> dict:
    """Generates theme-matched low-level, mid-level, and boss encounters with loot, armor, and lore unlocks."""
    theme_encounters = lang_data.get("theme_encounters", {})
    encounters = theme_encounters.get(chosen_theme_name)
    
    if not encounters:
        # Fallback if theme not found
        encounters = theme_encounters.get(list(theme_encounters.keys())[0])
        
    return encounters

# ==========================================
# HELPER DATA FOR COMBAT & INVENTORY
# ==========================================

def generate_character_combat_and_inventory(cls: str, subclass: str, race: str, bg: str, stats: dict, is_es: bool) -> dict:
    """Generates Combat, Weaponry, Inventory, and Magic info based on class, subclass, race, and background."""
    
    # Calculate HP: Hit Die Base + Con Modifier
    con_mod = int(stats["CON"]["mod"])
    dex_mod = int(stats["DEX"]["mod"])
    
    hit_dice_map = {
        "Fighter": 10, "Guerrero": 10,
        "Wizard": 6, "Mago": 6,
        "Rogue": 8, "Pícaro": 8,
        "Cleric": 8, "Clérigo": 8,
        "Ranger": 10, "Explorador": 10,
        "Paladin": 10, "Paladín": 10,
        "Bard": 8, "Bardo": 8,
        "Druid": 8, "Druida": 8,
        "Warlock": 8, "Brujo": 8
    }
    base_hd = hit_dice_map.get(cls, 8)
    hp_val = max(1, base_hd + con_mod)
    
    # Base AC & Armor Map
    armor_map_en = {
        "Fighter": ("Chain Mail", 16, False),
        "Wizard": ("No Armor (Robes)", 10, True),
        "Rogue": ("Leather Armor", 11, True),
        "Cleric": ("Scale Mail & Shield", 16, False),
        "Ranger": ("Studded Leather Armor", 12, True),
        "Paladin": ("Chain Mail & Shield", 18, False),
        "Bard": ("Leather Armor", 11, True),
        "Druid": ("Hide Armor & Shield", 14, False),
        "Warlock": ("Leather Armor", 11, True)
    }
    
    armor_map_es = {
        "Guerrero": ("Cota de malla", 16, False),
        "Mago": ("Sin armadura (Túnicas)", 10, True),
        "Pícaro": ("Armadura de cuero", 11, True),
        "Clérigo": ("Cota de escamas y escudo", 16, False),
        "Explorador": ("Cuero tachonado", 12, True),
        "Paladín": ("Cota de malla y escudo", 18, False),
        "Bardo": ("Armadura de cuero", 11, True),
        "Druida": ("Armadura de pieles y escudo", 14, False),
        "Brujo": ("Armadura de cuero", 11, True)
    }
    
    amap = armor_map_es if is_es else armor_map_en
    armor_name, base_ac, add_dex = amap.get(cls, ("Leather Armor" if not is_es else "Armadura de cuero", 11, True))
    ac_val = base_ac + (dex_mod if add_dex else 0)
    
    # Initiative = DEX Mod
    init_val = stats["DEX"]["mod"]
    prof_val = "+2"
    
    # Main Attack
    main_attack_map_en = {
        "Fighter": "Longsword (+5 to hit, 1d8+3 slashing)",
        "Wizard": "Fire Bolt (+5 to hit, 1d10 fire damage) or Quarterstaff (+2 to hit, 1d6 bludgeoning)",
        "Rogue": "Rapier (+5 to hit, 1d8+3 piercing, Sneak Attack +1d6)",
        "Cleric": "Mace (+4 to hit, 1d6+2 bludgeoning) or Sacred Flame (DC 13 Dex, 1d8 radiant)",
        "Ranger": "Longbow (+5 to hit, 1d8+3 piercing) or Shortswords (+5 to hit, 1d6+3 slashing)",
        "Paladin": "Greatsword (+5 to hit, 2d6+3 slashing) or Divine Smite",
        "Bard": "Rapier (+4 to hit, 1d8+2 piercing) or Vicious Mockery (DC 13 Wis, 1d4 psychic)",
        "Druid": "Produce Flame (+4 to hit, 1d8 fire) or Scimitar (+3 to hit, 1d6+1 slashing)",
        "Warlock": "Eldritch Blast (+5 to hit, 1d10 force damage)"
    }
    main_attack_map_es = {
        "Guerrero": "Espada larga (+5 para impactar, 1d8+3 cortante)",
        "Mago": "Descarga de fuego (+5 para impactar, 1d10 fuego) o Bastón (+2 para impactar, 1d6 contundente)",
        "Pícaro": "Ropera (+5 para impactar, 1d8+3 perforante, Ataque furtivo +1d6)",
        "Clérigo": "Maza (+4 para impactar, 1d6+2 contundente) o Llama sagrada (CD 13 Dex, 1d8 radiante)",
        "Explorador": "Arco largo (+5 para impactar, 1d8+3 perforante) o Espadas cortas (+5 para impactar, 1d6+3 cortante)",
        "Paladín": "Mandoble (+5 para impactar, 2d6+3 cortante) o Castigo divino",
        "Bardo": "Ropera (+4 para impactar, 1d8+2 perforante) o Burla dañina (CD 13 Sab, 1d4 psíquico)",
        "Druida": "Producir llama (+4 para impactar, 1d8 fuego) o Cimitarra (+3 para impactar, 1d6+1 cortante)",
        "Brujo": "Descarga mística (+5 para impactar, 1d10 daño de fuerza)"
    }
    atk_map = main_attack_map_es if is_es else main_attack_map_en
    main_attack_val = atk_map.get(cls, "Unarmed Strike (+2 to hit, 1 bludgeoning)")
    
    # Starting Equipment
    eq_bg_en = {
        "Acolyte": "Prayer book, 5 sticks of incense, vestments, set of common clothes, 15 gp.",
        "Criminal": "Crowbar, set of dark common clothes with hood, belt pouch, 15 gp.",
        "Folk Hero": "Set of artisan's tools, shovel, iron pot, set of common clothes, belt pouch, 10 gp.",
        "Noble": "Set of fine clothes, signet ring, scroll of pedigree, purse containing 25 gp.",
        "Sage": "Ink bottle, quill, small knife, letter from a dead colleague, common clothes, pouch with 10 gp.",
        "Soldier": "Insignia of rank, trophy from a fallen enemy, set of bone dice, common clothes, belt pouch, 10 gp.",
        "Urchin": "Small knife, map of hometown, pet mouse, token from parents, common clothes, belt pouch, 10 gp.",
        "Outlander": "Staff, hunting trap, trophy from an animal, set of traveler's clothes, belt pouch, 10 gp."
    }
    eq_bg_es = {
        "Acólito": "Libro de oraciones, 5 varillas de incienso, vestiduras, ropa común, bolsa con 15 po.",
        "Criminal": "Palanca, juego de ropas oscuras comunes con capucha, bolsa de cinturón, 15 po.",
        "Héroe del Pueblo": "Juego de herramientas de artesano, pala, olla de hierro, ropa común, bolsa con 10 po.",
        "Noble": "Juego de ropas finas, anillo de sello, pergamino de linaje, monedero con 25 po.",
        "Sabio": "Frasco de tinta, pluma, cuchillo pequeño, carta de un colega difunto, ropa común, bolsa con 10 po.",
        "Soldado": "Insignia de rango, trofeo de un enemigo caído, juego de dados de hueso, ropa común, bolsa con 10 po.",
        "Gamberro": "Cuchillo pequeño, mapa de su ciudad natal, ratón mascota, recuerdo familiar, ropa común, 10 po.",
        "Forastero": "Bastón, trampa de caza, trofeo de un animal cazado, ropa de viajero, bolsa con 10 po."
    }
    bg_map = eq_bg_es if is_es else eq_bg_en
    bg_eq = bg_map.get(bg, "Traveler's clothes, belt pouch with 10 gp.")
    starting_eq = f"[{cls} Gear] Backpack, bedroll, mess kit, tinderbox, 10 torches, 10 days of rations, waterskin. [{bg}] {bg_eq}" if not is_es else f"[Equipo de {cls}] Mochila, saco de dormir, kit de cocina, yesca y pedernal, 10 antorchas, 10 días de raciones, cantimplora. [{bg}] {bg_eq}"
    
    # Magic / Spells
    magic_map_en = {
        "Wizard": f"Spellbook (Cantrips: Fire Bolt, Light, Mage Hand; 1st Level: Magic Missile, Shield, Sleep). Subclass ({subclass}): Feature unlocked.",
        "Cleric": f"Divine Spellcasting (Cantrips: Sacred Flame, Thaumaturgy, Guidance; 1st Level: Cure Wounds, Bless, Guiding Bolt). Domain ({subclass}).",
        "Warlock": f"Pact Magic (Cantrips: Eldritch Blast, Minor Illusion; 1st Level: Hellish Rebuke, Hex). Patron ({subclass}).",
        "Bard": f"Spellcasting (Cantrips: Vicious Mockery, Prestidigitation; 1st Level: Healing Word, Dissonant Whispers, Thunderwave). College ({subclass}).",
        "Druid": f"Druidic Magic & Wild Shape (Cantrips: Druidcraft, Produce Flame; 1st Level: Entangle, Cure Wounds). Circle ({subclass}).",
        "Ranger": f"Wilderness magic unlocks at Level 2. Specialized Focus ({subclass}). Racial Trait ({race}): Natural adaptability.",
        "Paladin": f"Divine Smite & Lay on Hands (Aura of Protection). Oath ({subclass}). Racial Trait ({race}): Blessed resilience.",
        "Fighter": f"Martial Superiority & Second Wind ({subclass}). No innate spellcasting unless Eldritch Knight (Cantrips: Blade Ward, Fire Bolt).",
        "Rogue": f"Sneak Attack & Cunning Action ({subclass}). No innate spellcasting unless Arcane Trickster (Cantrips: Mage Hand, Minor Illusion)."
    }
    magic_map_es = {
        "Guerrero": f"Superioridad marcial y Segundo aliento ({subclass}). Sin conjuros nativos salvo Caballero Arcano (Trucos: Salvaguarda, Descarga de fuego).",
        "Mago": f"Libro de conjuros (Trucos: Descarga de fuego, Luz, Mano de mago; Nivel 1: Proyectil mágico, Escudo, Sueño). Subclase ({subclass}).",
        "Pícaro": f"Ataque furtivo y Acción astuta ({subclass}). Sin conjuros nativos salvo Embaucador Arcano (Trucos: Mano de mago, Ilusión menor).",
        "Clérigo": f"Lanzamiento de conjuros divinos (Trucos: Llama sagrada, Taumaturgia, Guía; Nivel 1: Curar heridas, Bendición, Saeta guiada). Dominio ({subclass}).",
        "Explorador": f"La magia de la naturaleza se desbloquea en nivel 2. Enfoque especial ({subclass}). Rasgo racial ({race}): Adaptabilidad natural.",
        "Paladín": f"Castigo divino y Imposición de manos. Juramento ({subclass}). Rasgo racial ({race}): Resiliencia bendita.",
        "Bardo": f"Lanzamiento de conjuros (Trucos: Burla dañina, Prestidigitación; Nivel 1: Palabra de curación, Susurros disonantes, Onda de trueno). Colegio ({subclass}).",
        "Druida": f"Magia druídica y Forma salvaje (Trucos: Artimaña druídica, Producir llama; Nivel 1: Entrañar, Curar heridas). Círculo ({subclass}).",
        "Brujo": f"Magia de pacto (Trucos: Descarga mística, Ilusión menor; Nivel 1: Reprensión infernal, Manto de espinas/Hex). Patrón ({subclass})."
    }
    mmap = magic_map_es if is_es else magic_map_en
    magic_val = mmap.get(cls, f"No innate spellcasting. Subclass ({subclass}) abilities active.")
    
    return {
        "hp": str(hp_val),
        "ac": str(ac_val),
        "initiative": init_val,
        "proficiency": prof_val,
        "equipped_armor": armor_name,
        "main_attack": main_attack_val,
        "starting_equipment": starting_eq,
        "magic_spells": magic_val
    }

# ==========================================
# EXTENDED STORY GENERATOR (4 STORIES PER THEME)
# ==========================================

def generate_extended_story(theme_key: str, theme_name: str, faction_a: str, faction_b: str, primary_settlement: str, secondary_settlement: str, is_es: bool) -> str:
    """Randomly selects 1 of 4 narrative stories for the given universe theme."""
    
    if is_es:
        stories = {
            "1": [
                (
                    f"Durante décadas, la revolución industrial mágica alimentó los motores de latón de {primary_settlement}. Sin embargo, la brecha de ideals entre {faction_a} y {faction_b} ha fracturado el monopolio del éter purificado que impulsa la maquinaria del asentamiento clave {secondary_settlement}.",
                    f"El conflicto estalló cuando {faction_a} patentó un motor de transmutación capaz de sintetizar vapor arcano a costa del suministro subterráneo regional. {faction_b} movilizó sus autómatas y sabotearon las tuberías maestras de {primary_settlement}, argumentando que la sobrepresión causará una explosión cataclísmica en toda la cuenca.",
                    f"Las calles están cubiertas de humo denso y engranajes marchitos. Mientras {faction_a} fortifica {primary_settlement} con tanques de presión arcana, operarios de {faction_b} reclutan saboteadores en {secondary_settlement}. El calderero central cruje bajo tensiones insostenibles, dejando el destino de la era del vapor en manos de héroes audaces."
                ),
                (
                    f"En los cielos oscurecidos por el hollín sobre {primary_settlement}, los dirigibles armados del {faction_a} patrullan incesantemente. La chispa de la rebelión ha sido encendida por el {faction_b}, bloqueando la refinería de bronce que abastece a {secondary_settlement}.",
                    f"Todo comenzó cuando un autómata autoconsciente robó los planos del Generador Ígneo en los talleres de {primary_settlement}. {faction_a} acusa al {faction_b} de albergar la máquina fugitiva, mientras que estos afirman que la creación de inteligencia artificial mística destruirá el valor del trabajo humano en {secondary_settlement}.",
                    f"Entre el estruendo de engranajes y descargas de vapor a presión, cazadores de recompensas y mecánicos se baten en combate. {faction_a} prepara un asedio masivo sobre los distritos industriales de {primary_settlement}, mientras el {faction_b} arma a los trabajadores en {secondary_settlement} para un levantamiento inevitable."
                ),
                (
                    f"Las catacumbas de cobre de {primary_settlement} esconden un antiguo motor alquímico recién desenterrado. La despiadada competencia entre el {faction_a} y el {faction_b} ha paralizado el transporte neumático hacia {secondary_settlement}.",
                    f"Al activar el artefacto, una plaga de herrumbre mágica comenzó a corroer los puentes y máquinas de {primary_settlement}. {faction_a} culpa al {faction_b} de sabotaje intencional, mientras que el {faction_b} asegura que el motor es una reliquia maldita que infectará las minas de {secondary_settlement}.",
                    f"Las tuberías gotean ácido y la niebla metálica asfixia los bulevares. Mientras el {faction_a} envía legionarios de hierro a {primary_settlement}, aventureros financiados por el {faction_b} buscan el núcleo purificador en {secondary_settlement} antes de que la ciudad se desmorone."
                ),
                (
                    f"Un descubrimiento astronómico desde la Gran Espira de {primary_settlement} ha revelado un cometa de cuarzo arcano cayendo cerca de {secondary_settlement}. La carrera encarnizada entre el {faction_a} y el {faction_b} amenaza con desencadenar una guerra total.",
                    f"El {faction_a} desplegó sus fortalezas flotantes a vapor para reclamar el cometa y monopolizar su energía. Sin embargo, el {faction_b} instaló cañones de vapor de largo alcance en {primary_settlement} para derribar las naves enemigas antes de que lleguen a {secondary_settlement}.",
                    f"Lluvia de ceniza dorada y chispas de latón caen sobre las metrópolis. Mientras el {faction_a} recluta pilotos de dirigible en {primary_settlement}, mercenarios del {faction_b} se abren paso entre la selva de tuberías en {secondary_settlement} para asegurar el impacto."
                )
            ],
            "2": [
                (
                    f"Tras la Gran Ruptura Arcana, los páramos desolados alrededor de {primary_settlement} quedaron cubiertos por una ceniza tóxica y radiactiva. La guerra por el agua limpia y los artefactos pre-colapso contrapone agresivamente a {faction_a} contra {faction_b}, bloqueando el paso hacia {secondary_settlement}.",
                    f"La crisis comenzó tras desenterrar un reactor de maná intacto bajo el lecho seco de {primary_settlement}. {faction_a} busca detonar la reliquia para erradicar las mutaciones salvajes, mientras que {faction_b} intenta canalizar el maná para canalizar vida sintética a los cultivos enfermos de {secondary_settlement}.",
                    f"En una tierra devastada por tormentas de fuego místico, las escaramuzas violentas son cotidianas. Mientras {faction_a} atrinchera sus bunkers en {primary_settlement}, exploradores de {faction_b} reclutan cazadores de la chatarra para tomar el reactor. La radiación mágica aumenta cada hora, acorralando el futuro de los sobrevivientes."
                ),
                (
                    f"En las ruinas sumergidas en polvo de {primary_settlement}, bandas de saqueadores rinden culto a la magia distorsionada. El conflicto brutal entre el {faction_a} y el {faction_b} destruyó los últimos pozos no contaminados de {secondary_settlement}.",
                    f"Un mutante con poderes psiónicos emergió del Cráter del Vacío en {primary_settlement}, atrayendo devotos de todas partes. El {faction_a} exige su ejecución para evitar la corrupción final, mientras que el {faction_b} lo considera el nuevo mesías de la era mística en {secondary_settlement}.",
                    f"Monstruosidades deformadas por la magia vagan por las autopistas derruidas. Mientras el {faction_a} prepara sus purificadores flamígeros en {primary_settlement}, células del {faction_b} asaltan los arsenales en {secondary_settlement} para provocar una erupción mágica irreversible."
                ),
                (
                    f"Una tormenta de maná salvaje se ha estancado sobre las torres rotas de {primary_settlement}. La desesperada búsqueda de escudos rúnicos contrapone al {faction_a} con el {faction_b}, aislando a la golpeada población de {secondary_settlement}.",
                    f"El {faction_a} ha comenzado a sacrificar reliquias arcanas antiguas para levantar una cúpula sobre {primary_settlement}, dejando a los poblados vecinos indefensos. El {faction_b} se ha alzado en armas, amenazando con destruir los generadores del escudo en {secondary_settlement} para que todos compartan el mismo destino.",
                    f"Rayos violetas y lluvia ácida desgarran los cielos de la desolación. Mientras el {faction_a} recluta mercenarios pesados en {primary_settlement}, guerrilleros del {faction_b} sabotean las torres mágicas en {secondary_settlement} antes de que la tormenta arrase con todo."
                ),
                (
                    f"Bajo las ruinas de la antigua biblioteca arcana de {primary_settlement}, se halló el Grimorio del Fin. La lucha encarnizada por su lectura entre el {faction_a} y el {faction_b} ha paralizado el refugio de {secondary_settlement}.",
                    f"El {faction_a} afirma que el texto contiene la fórmula para restaurar la tierra como era antes del cataclismo. No obstante, el {faction_b} sostiene que leer el pergamino invocará a los titanes que destruyeron el mundo en {secondary_settlement}.",
                    f"Cultistas de la chatarra y soldados de fortuna cruzan fuego entre los cascarones de hormigón. Mientras el {faction_a} atrinchera a sus eruditos en {primary_settlement}, comandos del {faction_b} avanzan desde {secondary_settlement} para incinerar el libro a toda costa."
                )
            ],
            "3": [
                (
                    f"Bajo un cielo donde el sol murió hace siglos, el mar abisal susurra oscuros secretos en los muelles oscuros de {primary_settlement}. La paz relativa se ha quebrado por la disputa total entre {faction_a} y {faction_b} por el control de los faros bioluminiscentes que conectan con {secondary_settlement}.",
                    f"El horror despertó cuando {faction_a} comenzó a cosechar la sangre de los leviatanes abisales hundidos cerca de {primary_settlement} para encender sus quinqués e iluminar la costa. {faction_b} afirma que la masacre ha despertado a una entidad primordial del abismo que engullirá {secondary_settlement} si no se detiene el ritual.",
                    f"Entre la niebla helada y las mareas de tinta negra, la locura consume a los marineros. {faction_a} arma sus acorazados de hierro en {primary_settlement}, mientras agentes de {faction_b} reclutan corsarios de la penumbra en {secondary_settlement}. El leviatán brama desde las profundidades, esperando una chispa para hundir el mundo."
                ),
                (
                    f"Las aguas gélidas y sin sol de {primary_settlement} han comenzado a congelarse, atrapando a las flotas pesqueras en hielo negro. El enfrentamiento feroz entre el {faction_a} y el {faction_b} ha bloqueado la única ruta cálida hacia {secondary_settlement}.",
                    f"Surgió un naufragio fantasma en las costas de {primary_settlement} cargado de ídolos de perla negra. El {faction_a} busca subastar los objetos para financiar barcos rompehielos, pero el {faction_b} declara que los ídolos están malditos y provocaron el congelamiento del mar en {secondary_settlement}.",
                    f"Campanas de niebla e himnos siniestros resonaron en los puertos oscuros. Mientras el {faction_a} refuerza la guardia en {primary_settlement}, marineros desesperados al servicio del {faction_b} intentan hundir la nave fantasma desde {secondary_settlement} antes de que el hielo sepulte la bahía."
                ),
                (
                    f"Un extraño canto coral emerge del vórtice profundo cercano a {primary_settlement}, induciendo el trance a los habitantes costeros. El enfrentamiento entre el {faction_a} y el {faction_b} paralizó los muelles clave de {secondary_settlement}.",
                    f"El {faction_a} intenta construir campanas sumergibles gigantes en {primary_settlement} para descender al origen de la voz. Sin embargo, el {faction_b} sabotea los astilleros, afirmando que despertar a los sirenos antiguos sumergirá a {secondary_settlement} bajo una marea eterna.",
                    f"Criaturas de las profundidades escalan por los pilotes de madera. Mientras el {faction_a} contrata buzos blindados en {primary_settlement}, agentes cultistas del {faction_b} infiltran los santuarios de {secondary_settlement} para sellar los oídos de la población con cera mística."
                ),
                (
                    f"Mareas rojas de algas carnívoras invadieron las aguas místicas de {primary_settlement}, matando la fauna marina. La guerra de recursos entre el {faction_a} y el {faction_b} ahoga la economía del puerto exterior en {secondary_settlement}.",
                    f"El {faction_a} descubrió que las algas pueden procesarse para crear un combustible marino revolucionario en {primary_settlement}. El {faction_b} denuncia que cultivar las algas acidifica el agua y envenena las reservas de agua dulce de {secondary_settlement}.",
                    f"Vapor de alquitrán y olor a azufre flotan en el ambiente. Mientras el {faction_a} patrulla las cosechas en {primary_settlement}, guerrilleros del {faction_b} lanzan teas incansables desde {secondary_settlement} para purificar el mar con fuego."
                )
            ],
            "4": [
                (
                    f"Flotando sobre un abismo infinito, los archipiélagos celestes de {primary_settlement} dependen de los cristales de levitación. La frágil alianza entre {faction_a} y {faction_b} se ha destrozado, poniendo en peligro los puentes de viento que abastecen a {secondary_settlement}.",
                    f"La catástrofe comenzó cuando {faction_a} intentó extraer el núcleo gravitatorio enterrado en la base de {primary_settlement}. {faction_b} reaccionó enviando flotillas de barcos voladores para bloquear la excavación, advirtiendo que la pérdida de masa hará que las islas caigan para siempre al abismo inferior.",
                    f"Vientos huracanados y tormentas de éter azotan los muelles flotantes. Mientras {faction_a} instala arpones pesados en {primary_settlement}, mercenarios de {faction_b} reclutan navegantes de los cielos en {secondary_settlement}. Las islas han comenzado a perder altitud dramáticamente, exigiendo una resolución inmediata."
                ),
                (
                    f"Una falla en las corrientes de viento primarias rodea la isla cumbre de {primary_settlement}, haciendo imposible la navegación convencional. La disputa armada entre el {faction_a} y el {faction_b} ha dejado varadas a las colonias de {secondary_settlement}.",
                    f"El {faction_a} capturó a una bestia celestialmente mítica capaz de calmar los vendavales en {primary_settlement}. El {faction_b} movilizó piratas para liberar a la criatura, sosteniendo que encadenarla alterará las corrientes continentales y provocará choques entre las islas de {secondary_settlement}.",
                    f"Barcos de vela solar chocan en medio de nubes de tormenta. Mientras el {faction_a} fortifica la celda astral en {primary_settlement}, audaces corsarios del {faction_b} planifican un abordaje aéreo desde los muelles de {secondary_settlement}."
                ),
                (
                    f"Fragmentos de las islas flotantes superiores han comenzado a colisionar con los sectores residenciales de {primary_settlement}. El conflicto político entre el {faction_a} y el {faction_b} bloqueó la evacuación hacia {secondary_settlement}.",
                    f"El {faction_a} propone volar mediante cargas explosivas las islas flotantes descontroladas que amenazan {primary_settlement}. No obstante, el {faction_b} se opone firmemente, revelando que esas tierras flotantes albergan a los ancestros de {secondary_settlement}.",
                    f"Lluvia de rocas y cristales rotos cae sobre el abismo. Mientras el {faction_a} posiciona cañones pesados en {primary_settlement}, activistas del {faction_b} aseguran las amarras mágicas en {secondary_settlement} para evitar la destrucción del patrimonio celestial."
                ),
                (
                    f"Un portal de éter inestable se abrió en los cielos superiores de {primary_settlement}, atrayendo tormentas electromagnéticas. La feroz competencia por estabilizarlo contrapone al {faction_a} contra el {faction_b}, amenazando a {secondary_settlement}.",
                    f"El {faction_a} intenta canalizar el portal para abrir rutas celestes comercio a otros mundos desde {primary_settlement}. El {faction_b} busca sellarlo de inmediato, temiendo que criaturas del vacío exterior invadan las ciudades de {secondary_settlement}.",
                    f"Relámpagos dorados cruzan el firmamento resquebrajado. Mientras el {faction_a} junta a sus magos celestes en {primary_settlement}, defensores del {faction_b} preparan runas de sellado en {secondary_settlement} antes de que el portal se expanda irrecuperablemente."
                )
            ],
            "5": [
                (
                    f"Bajo dos soles abrasadores, las dunas doradas que rodean el oasis de {primary_settlement} guardan tumbas de reyes olvidados. Las tensiones geopolíticas entre {faction_a} y {faction_b} han paralizado las caravanas de especias y agua que sustentan al puesto distante de {secondary_settlement}.",
                    f"El conflicto estalló al abrirse la Tumba del Faraón Sol en {primary_settlement}, revelando un amuleto capaz de dominar las tormentas de arena. {faction_a} pretende usarlo para marchar sobre las ciudades libres, mientras que {faction_b} busca sepultar la reliquia para evitar que despierte la antigua maldición del desierto sobre {secondary_settlement}.",
                    f"Los espejismos se mezclan con el chocar de acero sobre la arena caliente. {faction_a} atrincheró sus legiones alrededor de {primary_settlement}, mientras {faction_b} reúne nómadas e infiltrados en {secondary_settlement}. La tormenta de arena se aproxima en el horizonte, amenazando con sepultar toda civilización."
                ),
                (
                    f"El gran acuífero subterráneo bajo el desierto de {primary_settlement} ha comenzado a secarse rápidamente. La lucha despiadada por el recurso vital contrapone al {faction_a} contra el {faction_b}, poniendo en riesgo la vida en {secondary_settlement}.",
                    f"El {faction_a} tomó el control de los pozos profundos de {primary_settlement} para racionar el agua a cambio de lealtad absoluta. El {faction_b} respondió destruyendo los acueductos imperiales, prometiendo liberar las aguas para todos los pueblos de {secondary_settlement}.",
                    f"Sol ardiente y sed insoportable ahogan a la población. Mientras el {faction_a} mantiene a tiro de ballesta los pozos de {primary_settlement}, nómadas del {faction_b} organizan incursiones nocturnas desde los oasis de {secondary_settlement}."
                ),
                (
                    f"Gusanos de arena gigantescos impulsados por magia primigenia han despertado en el mar de dunas cercano a {primary_settlement}. La discrepancia en el método para eliminarlos entre el {faction_a} y el {faction_b} aisló a {secondary_settlement}.",
                    f"El {faction_a} pretende envenenar los pozos de especias de {primary_settlement} para exterminar a las bestias. El {faction_b} argumenta que las criaturas son sagradas y que matarlas colapsará los ecosistemas subterráneos de {secondary_settlement}.",
                    f"El suelo tiembla bajo rugidos cavernosos. Mientras el {faction_a} prepara catapultas alquímicas en {primary_settlement}, marianos y chamanes del {faction_b} realizan danzas rituales en {secondary_settlement} para desviar a los gusanos."
                ),
                (
                    f"Un eclipse solar eterno ha sumido al desierto de {primary_settlement} en un frío sepulcral insólito. La disputa por la reliquia solar contrapone brutalmente al {faction_a} y al {faction_b}, helando los pozos de {secondary_settlement}.",
                    f"El {faction_a} acusa al {faction_b} de usar nigromancia para robar la chispa solar del gran templo de {primary_settlement}. El {faction_b} demuestra que el sacerdote supremo del {faction_a} vendió la chispa a sombras oscuras para obtener inmortalidad en {secondary_settlement}.",
                    f"Vientos gélidos y dunas heladas desorientan a los viajeros. Mientras el {faction_a} patrulla los templos de {primary_settlement}, paladines del {faction_b} buscan el núcleo térmico escondido en {secondary_settlement} para devolver el calor al mundo."
                )
            ],
            "6": [
                (
                    f"Durante siglos, la región de {primary_settlement} floreció en relativa calma bajo el influjo del estilo {theme_name}. Sin embargo, la fractura ideológica entre {faction_a} y {faction_b} ha desestabilizado las rutas comerciales y las redes arcanas que alimentan a los asentamientos clave como {secondary_settlement}.",
                    f"El conflicto escaló cuando {faction_a} descubrió una reserva olvidada de energía mística bajo los cimientos de {primary_settlement}. Intentando monopolizar esta fuente irreemplazable, movilizaron sus fuerzas armadas, provocando una respuesta inmediata de {faction_b}, quienes afirman que alterar dicho flujo traerá un cataclismo irreparable sobre el ecosistema y la estabilidad política de toda la región.",
                    f"En la actualidad, las escaramuzas urbanas y el espionaje amenazan con derivar en una conflagración abierta. Mientras {faction_a} fortifica {primary_settlement}, agentes de {faction_b} reclutan aventureros e incursionan en {secondary_settlement} para asegurar artefactos clave. La reserva energética se vuelve inestable cada día que pasa, dejando el destino de la región en manos de aquellos audaces capaces de inclinarse por una causa o forjar un nuevo camino."
                ),
                (
                    f"Las torres de biocristal y los jardines flotantes de {primary_settlement} sufren una plaga de esporas fúngicas luminiscentes. La tensión política entre el {faction_a} y el {faction_b} ha detenido la cura que esperaba el poblado de {secondary_settlement}.",
                    f"El {faction_a} planea quemar los sectores agrícolas infectados de {primary_settlement} mediante rayos solares concentrados. El {faction_b} sostiene que la plaga es una respuesta natural del bosque y busca adaptar genéticamente la flora mística de {secondary_settlement}.",
                    f"Luz bioluminiscente parpadea en las copas de los árboles gigantes. Mientras el {faction_a} despliega sus prismas de fuego en {primary_settlement}, eco-magos del {faction_b} distribuyen antitoxinas naturales en {secondary_settlement} para proteger los cultivos."
                ),
                (
                    f"Un fallo en la red foto-arcana que ilumina las cúpulas de vegetación de {primary_settlement} amenaza con hundir la canopia en la oscuridad. El enfrentamiento por los cristales foto-voltaicos contrapone al {faction_a} con el {faction_b}, afectando a {secondary_settlement}.",
                    f"El {faction_a} intenta acaparar los generadores solares de {primary_settlement} para garantizar energía únicamente a las cúpulas centrales. El {faction_b} inició un sabotaje masivo para reconectar la energía a las comunidades periféricas de {secondary_settlement}.",
                    f"Sombras inéditas caen sobre la jungla tecnológica. Mientras el {faction_a} custodia los paneles de luz en {primary_settlement}, ingenieros botánicos del {faction_b} conectan raíces místicas en {secondary_settlement} para encender bioluminiscencia de emergencia."
                ),
                (
                    f"El Gran Árbol Madre en cuyo tronco se construyó {primary_settlement} ha comenzado a petrificarse misteriosamente. La lucha entre el {faction_a} y el {faction_b} impide el acceso a la savia curativa necesaria en {secondary_settlement}.",
                    f"El {faction_a} afirma que la inyección de catalizadores sintéticos salvo la vida del árbol en {primary_settlement}. Sin embargo, el {faction_b} demuestra que los químicos están acelerando la petrificación para extraer madera de piedra preciosa hacia {secondary_settlement}.",
                    f"Hojas de vidrio y ramas de cuarzo crujen con el viento. Mientras el {faction_a} protege las bombas de inyección en {primary_settlement}, druidas cibernéticos del {faction_b} buscan el germen puro en {secondary_settlement} para plantar un nuevo núcleo."
                )
            ],
            "7": [
                (
                    f"En los bosques oscuro rodeados de niebla donde yace {primary_settlement}, el susurro de pactos prohibidos resuena en cada rincón. La confrontación directa entre {faction_a} y {faction_b} ha roto la tregua milenaria que protegía los arcanos del coven y la red mágica de {secondary_settlement}.",
                    f"El detonante fue el descubrimiento del Libro de las Sombras Primigenias en {primary_settlement}. {faction_a} busca invocar a una entidad estelar para obtener poder absoluto, mientras que {faction_b} insiste en que romper los sellos liberará una plaga demoníaca que devorará las almas de {secondary_settlement}.",
                    f"Las velas de sebo arden con fuego verde y los cuervos vigilan los caminos. Mientras {faction_a} prepara el gran ritual en {primary_settlement}, cazadores de sombras ligados a {faction_b} se reúnen en {secondary_settlement}. El eclipse de luna de sangre se acerca, marcando el límite para detener el pacto supremo."
                ),
                (
                    f"Un pozo de azufre y sombras emergió en la plaza central de {primary_settlement}, atrayendo demonios menores de otros planos. La lucha desesperada entre el {faction_a} y el {faction_b} paralizó el comercio de ingredientes mágicos con {secondary_settlement}.",
                    f"El {faction_a} pactó con un señor del averno para controlar las huestes demoníacas y defender {primary_settlement}. El {faction_b} se opuso radicalmente, organizando patrullas de purificación para exorcisar los pozos en {secondary_settlement} antes de que el portal se abra definitivamente.",
                    f"Olor a azufre y susurros infernales llenan las vísperas. Mientras el {faction_a} fortifica las laderas de {primary_settlement}, brujos rebeldes del {faction_b} reúnen amuletos de plata en {secondary_settlement} para sellar las fisuras."
                ),
                (
                    f"La matriarca del aquelarre dominante en {primary_settlement} ha sido asesinada con una daga de mandrágora blanca. La sangrienta cacería de brujas desencadenada entre el {faction_a} y el {faction_b} aterroriza a los pobladores de {secondary_settlement}.",
                    f"El {faction_a} culpa al círculo de brujos de {secondary_settlement} e inició arrestos masivos en {primary_settlement}. El {faction_b} afirma que la matriarca fue traicionada por sus propios acólitos para apoderarse de sus tierras de pacto.",
                    f"Muérdago seco y símbolos sangrientos marcan las puertas. Mientras el {faction_a} quema chozas en {primary_settlement}, inquisidores renegados del {faction_b} protegen a los sabios refugiados en {secondary_settlement} mientras investigan el crimen."
                ),
                (
                    f"Una niebla de pesadilla que causa alucinaciones mortales brotó de los pantanos vecinos a {primary_settlement}. El choque sangriento por el amuleto lunar contrapone al {faction_a} contra el {faction_b}, amenazando a {secondary_settlement}.",
                    f"El {faction_a} intenta usar la niebla como arma biológica mística para someter las villas de {primary_settlement}. El {faction_b} lucha por sintetizar un antídoto usando la raíz del sauce negro de {secondary_settlement}.",
                    f"Fantasmas y sombras danzan entre las arboledas deshojadas. Mientras el {faction_a} patrulla los pantanos de {primary_settlement}, herboristas y pactistas del {faction_b} recolectan flores nocturnas en {secondary_settlement} contra reloj."
                )
            ],
            "8": [
                (
                    f"En los majestuosos salones teñidos de rojo de {primary_settlement}, la alta cuna de la aristocracia inmortal celebra banquetes mientras la plebe se desangra. La guerra encubierta entre {faction_a} y {faction_b} amenaza con destruir el delicado equilibrio de poder con la urbe vecina de {secondary_settlement}.",
                    f"La disputa estalló por la escasez del 'Elixir Sanguíneo Puro', conservado bajo las criptas de {primary_settlement}. {faction_a} intenta restringir el consumo a la alta nobleza, mientras {faction_b} conspira para infectar los pozos de agua de {secondary_settlement} y convertir a la población en un ejército de siervos sedientos.",
                    f"Clices de copas de cristal y duelistas en la sombra marcan la vida nocturna. Mientras {faction_a} asegura las criptas de {primary_settlement}, infiltrados de {faction_b} reclutan mercenarios vivos en {secondary_settlement}. La noche se vuelve eterna y el olor a sangre fresca satura las calles."
                ),
                (
                    f"Un cazador de vampiros legendario fue capturado y exhibido en la estaca de la plaza de {primary_settlement}. El intento de rescate por parte del {faction_b} contra las fuerzas leales del {faction_a} convirtió la noche en una carnicería que afecta a {secondary_settlement}.",
                    f"El {faction_a} planea ejecutar al cazador en un ritual de luna llena en {primary_settlement} para absorber su inmunidad a la luz solar. El {faction_b} busca liberarlo a cambio de los secretos para destruir a los condes ancianos de {secondary_settlement}.",
                    f"Sábanas de terciopelo y manchas de sangre decoran las calzadas de piedra. Mientras el {faction_a} vigila las almenas de {primary_settlement}, cazadores rebeldes del {faction_b} se infiltran desde {secondary_settlement} armados con estacas de fresno."
                ),
                (
                    f"La plaga del 'Sudor de Plata', letal para los vampiros de sangre pura, se expande por las cortes de {primary_settlement}. La sangrienta lucha por los frascos de medicina alquímica contrapone al {faction_a} con el {faction_b}, desestabilizando {secondary_settlement}.",
                    f"El {faction_a} acusa al {faction_b} de crear la plaga biológica para exterminar a la realeza en {primary_settlement}. El {faction_b} sostiene que la plaga es un castigo divino por la tiranía ejercida sobre los mortales de {secondary_settlement}.",
                    f"Carrozas negras con cortinas tupidas cruzan los puentes a medianoche. Mientras el {faction_a} aisla los palacios de {primary_settlement}, médicos de la peste aliados al {faction_b} buscan el paciente cero en {secondary_settlement}."
                ),
                (
                    f"Se ha convocado el Gran Cónclave de las Catorce Familias Inmortales en la fortaleza de {primary_settlement}. Un complot de asesinato entre el {faction_a} y el {faction_b} amenaza con desencadenar una guerra entre condados hacia {secondary_settlement}.",
                    f"El {faction_a} intenta proclamar un rey absoluto para unir todas las cortes bajo la bandera de {primary_settlement}. El {faction_b} ha colocado explosivos de polvo de alquimia en los cimientos para erradicar a las familias y liberar {secondary_settlement}.",
                    f"Murciélagos de carga y mensajeros de la noche llenan los cielos góticos. Mientras el {faction_a} refuerza la guardia de honor en {primary_settlement}, espías del {faction_b} ultiman la mecha en los túneles subterráneos de {secondary_settlement}."
                )
            ],
            "9": [
                (
                    f"A lo largo de las prósperas rutas mercantiles centradas en {primary_settlement}, caravanas cargadas de sedas místicas y especias arcanas generan riquezas incalculables. La feroz competencia comercial entre {faction_a} y {faction_b} ha bloqueado los pasos de montaña hacia {secondary_settlement}.",
                    f"El conflicto alcanzó su punto crítico cuando una partida de mercaderes descubrió la mítica 'Especia del Loto Dorado' cerca de {primary_settlement}, capaz de otorgar la inmortalidad. {faction_a} ha acaparado el monopolio mediante impuestos abusivos, mientras {faction_b} financia piratas de la ruta para saquear los envíos a {secondary_settlement}.",
                    f"Mercados de exóticas telas, venenos y guardias armados llenan los bazares. Mientras {faction_a} fortifica los caravasares de {primary_settlement}, agentes de {faction_b} contratan contrabandistas en {secondary_settlement}. Con las rutas cerradas y las mercancías pudriéndose, el imperio comercial está a punto de colapsar."
                ),
                (
                    f"Una flota de juncos voladores cargados de seda de dragón llegó al puerto fluvial de {primary_settlement}. La disputa violenta por los derechos de aduana entre el {faction_a} y el {faction_b} ha desatado incendios en los almacenes de {secondary_settlement}.",
                    f"El {faction_a} confiscó el cargamento aduciendo contrabando de reliquias en {primary_settlement}. El {faction_b} movilizó a los sindicatos de marineros para sitiar las torres de aduana, prometiendo distribuir la seda entre los artesanos golpeados de {secondary_settlement}.",
                    f"El aroma a canela quemada y la seda roja ardiendo llenan el aire. Mientras el {faction_a} despliega sus mercenarios de la guardia dorada en {primary_settlement}, piratas de río del {faction_b} asaltan los arsenales náuticos de {secondary_settlement}."
                ),
                (
                    f"La falsificación masiva de la moneda imperial de jade ha provocado la quiebra de los bancos en {primary_settlement}. La cacería de los falsificadores contrapone encarnizadamente al {faction_a} contra el {faction_b}, sumiendo en la pobreza a {secondary_settlement}.",
                    f"El {faction_a} culpa a los gremios de alquimistas de {secondary_settlement} y bloqueó los mercados de {primary_settlement}. El {faction_b} demuestra que los altos ministros del {faction_a} emitieron la moneda falsa para financiar sus guerras personales.",
                    f"Bazares desiertos y guardias exigiendo tributos de sangre marcan el panorama. Mientras el {faction_a} ejecuta sospechosos en {primary_settlement}, contadores e infiltrados del {faction_b} intentan rescatar las reservas de jade puro escondidas en {secondary_settlement}."
                ),
                (
                    f"Se ha descubierto una nueva ruta marítima de especias que acorta el viaje entre {primary_settlement} y {secondary_settlement}. La guerra de corso desatada entre el {faction_a} y el {faction_b} ha llenado el mar de naufragios en llamas.",
                    f"El {faction_a} construyó fortalezas de piedra en las islas del estrecho para cobrar peaje a las naves de {primary_settlement}. El {faction_b} equipó navíos corsarios armados con fuego alquímico para destruir los baluartes y declarar la ruta libre hacia {secondary_settlement}.",
                    f"Velas de jade y banderas negras combaten entre arrecifes de coral. Mientras el {faction_a} refuerza sus cañones marinos en {primary_settlement}, corsarios del {faction_b} reclutan capitanes audaces en los puertos de {secondary_settlement} para romper el bloqueo."
                )
            ]
        }
    else:
        stories = {
            "1": [
                (
                    f"For decades, the magical industrial revolution powered the brass engines of {primary_settlement}. However, a bitter ideological split between {faction_a} and {faction_b} has shattered the monopoly on purified ether supplying key settlements like {secondary_settlement}.",
                    f"The crisis erupted when {faction_a} patented a transmutation engine that generates arcane steam by draining regional subterranean wells. {faction_b} deployed war-automata to sabotage the main pipelines of {primary_settlement}, claiming overpressure will cause a cataclysmic explosion.",
                    f"Thick smog and discarded gears blanket the streets. As {faction_a} fortifies {primary_settlement} with pressure tanks, operatives from {faction_b} recruit saboteurs in {secondary_settlement}. The central boiler groans under immense stress, leaving the steam age's fate to brave adventurers."
                ),
                (
                    f"In the soot-choked skies above {primary_settlement}, armed airships of {faction_a} maintain an unyielding blockade. The sparks of rebellion were ignited by {faction_b}, halting the bronze refinery feeding {secondary_settlement}.",
                    f"It all began when a self-aware automaton stole the designs for the Ignis Generator from workshops in {primary_settlement}. {faction_a} accuses {faction_b} of sheltering the runaway machine, while they claim mystical AI will render human labor worthless in {secondary_settlement}.",
                    f"Amidst screeching gears and bursts of pressurized steam, bounty hunters and grease-monkeys duel in alleyways. As {faction_a} prepares a massive siege on industrial districts in {primary_settlement}, {faction_b} arms factory workers in {secondary_settlement} for revolution."
                ),
                (
                    f"The copper catacombs beneath {primary_settlement} conceal a newly unearthed alchemical engine. Cutthroat rivalries between {faction_a} and {faction_b} have crippled the pneumatic transit system bound for {secondary_settlement}.",
                    f"Activating the device unleashed a plague of magical rust corroding bridges and machinery across {primary_settlement}. {faction_a} blames {faction_b} for intentional sabotage, while {faction_b} insists the engine is a cursed relic that will poison {secondary_settlement}'s mines.",
                    f"Acid leaks from pipes as metallic smog chokes the boulevards. While {faction_a} dispatches iron legionnaires to {primary_settlement}, adventurers funded by {faction_b} seek the purifying core in {secondary_settlement} before the city crumbles."
                ),
                (
                    f"An astronomical discovery atop the Grand Spire of {primary_settlement} revealed an arcane quartz comet hurtling toward {secondary_settlement}. The fierce race between {faction_a} and {faction_b} threatens to spark total war.",
                    f"{faction_a} deployed steam-dreadnoughts to claim the comet and monopolize its power. However, {faction_b} constructed long-range steam cannons in {primary_settlement} to blast enemy vessels before they reach {secondary_settlement}.",
                    f"Golden ash and brass sparks rain upon the metropolis. As {faction_a} recruits airship pilots in {primary_settlement}, mercenaries from {faction_b} fight through pipe-jungles in {secondary_settlement} to secure the crash site."
                )
            ],
            "2": [
                (
                    f"Following the Great Arcane Rupture, the wasteland surrounding {primary_settlement} was buried under toxic fallout. A desperate war for clean water and pre-collapse relics pits {faction_a} against {faction_b}, blocking vital passes to {secondary_settlement}.",
                    f"The spark was ignited when an intact mana-reactor was unearthed beneath {primary_settlement}. {faction_a} aims to detonate it to wipe out wild mutations, while {faction_b} seeks to channel the mana into reviving diseased crops near {secondary_settlement}.",
                    f"Violent skirmishes flare across the ruined landscape. As {faction_a} fortifies its bunkers in {primary_settlement}, {faction_b} scouts hire scrap-hunters in {secondary_settlement}. Arcane radiation builds by the hour, trapping all survivors in its wake."
                ),
                (
                    f"In the dust-buried ruins of {primary_settlement}, scavenger gangs worship warped magic. A brutal conflict between {faction_a} and {faction_b} destroyed the last uncorrupted wells in {secondary_settlement}.",
                    f"A psionic mutant emerged from the Void Crater in {primary_settlement}, attracting cultists from afar. {faction_a} demands his execution to prevent total corruption, while {faction_b} hails him as the savior of the wasteland in {secondary_settlement}.",
                    f"Twisted abominations roam collapsed highways. While {faction_a} readies flame-purifiers in {primary_settlement}, covert cells from {faction_b} raid armories in {secondary_settlement} to trigger an irreversible arcane eruption."
                ),
                (
                    f"A storm of wild mana has stalled over the shattered skyscrapers of {primary_settlement}. A frantic search for runic shields pits {faction_a} against {faction_b}, isolating the battered population of {secondary_settlement}.",
                    f"{faction_a} began sacrificing ancient relics to raise a barrier over {primary_settlement}, leaving neighboring settlements defenseless. {faction_b} took up arms, threatening to detonate generator towers in {secondary_settlement} so all share the same fate.",
                    f"Violet lightning and acid rain tear through bleak skies. As {faction_a} recruits heavy mercenaries in {primary_settlement}, guerrillas from {faction_b} sabotage magic towers in {secondary_settlement} before the storm wipes out everything."
                ),
                (
                    f"Beneath the ruins of {primary_settlement}'s arcana library, the Grimoire of the End was unearthed. The desperate struggle to translate it between {faction_a} and {faction_b} has paralyzed the sanctuary of {secondary_settlement}.",
                    f"{faction_a} claims the text holds the formula to restore the world to its pre-cataclysm state. However, {faction_b} warns that reading the scroll will unleash the titans that ruined {secondary_settlement}.",
                    f"Scrap cultists and soldiers of fortune exchange fire through concrete ruins. As {faction_a} barricades its scholars in {primary_settlement}, commandos from {faction_b} march from {secondary_settlement} to burn the book at all costs."
                )
            ],
            "3": [
                (
                    f"Under a sunless sky, the abyssal sea whispers dark secrets into the pitch-black docks of {primary_settlement}. Relative peace has shattered due to all-out war between {faction_a} and {faction_b} over bioluminescent lighthouses guiding ships to {secondary_settlement}.",
                    f"Horror awoke when {faction_a} began harvesting blood from sunken leviathans near {primary_settlement} to fuel their lanterns. {faction_b} claims this slaughter woke a primordial beast that will swallow {secondary_settlement} unless the ritual is stopped.",
                    f"Freezing mist and ink-black tides drive sailors to madness. As {faction_a} arms ironclad ships in {primary_settlement}, {faction_b} agents recruit shadowy corsairs in {secondary_settlement}. The leviathan stirs from the depths, awaiting a spark to drown the world."
                ),
                (
                    f"The freezing, sunless waters around {primary_settlement} have begun to lock in black ice, trapping fishing fleets. A bitter clash between {faction_a} and {faction_b} has sealed the only warm sea route to {secondary_settlement}.",
                    f"A phantom shipwreck washed ashore in {primary_settlement} laden with black pearl idols. {faction_a} seeks to auction them to build icebreaker ships, but {faction_b} claims the idols are cursed relics causing the sea to freeze near {secondary_settlement}.",
                    f"Foghorns and eerie sea shanties echo through darkened ports. While {faction_a} reinforces its harbor guard in {primary_settlement}, desperate sailors serving {faction_b} attempt to sink the ghost ship from {secondary_settlement} before ice buries the bay."
                ),
                (
                    f"An unsettling choral chant rises from the deep whirlpool near {primary_settlement}, mesmerizing coastal dwellers. The rivalry between {faction_a} and {faction_b} has paralyzed vital docks supplying {secondary_settlement}.",
                    f"{faction_a} attempts to construct colossal diving bells in {primary_settlement} to descend toward the source of the voice. However, {faction_b} sabotages the shipyards, insisting that waking ancient merfolk will submerge {secondary_settlement} under an eternal tide.",
                    f"Deep-sea monstrosities scale wooden piers. As {faction_a} hires armored divers in {primary_settlement}, cultist agents from {faction_b} infiltrate sanctuaries in {secondary_settlement} to seal citizens' ears with mystic wax."
                ),
                (
                    f"Red tides of carnivorous algae invaded the mystical waters of {primary_settlement}, killing off marine life. A resource war between {faction_a} and {faction_b} chokes the economy of {secondary_settlement}'s outer harbor.",
                    f"{faction_a} discovered that the algae can be refined into revolutionary marine fuel in {primary_settlement}. {faction_b} warns that farming the algae acidifies ocean waters and poisons freshwater reservoirs in {secondary_settlement}.",
                    f"Tar vapor and brimstone stench linger over the water. While {faction_a} patrols harvest fields in {primary_settlement}, guerrillas from {faction_b} launch firebrands from {secondary_settlement} to cleanse the sea with fire."
                )
            ],
            "4": [
                (
                    f"Floating over an endless void, the sky archipelagos of {primary_settlement} rely entirely on levitation crystals. The fragile truce between {faction_a} and {faction_b} has collapsed, severing the sky-bridges feeding {secondary_settlement}.",
                    f"Catastrophe loomed when {faction_a} attempted to mine the gravity core embedded in {primary_settlement}. {faction_b} dispatched airship fleets to blockade the site, warning that core extraction will send the islands crashing into the abyss.",
                    f"Gale-force winds and ether storms batter the floating docks. As {faction_a} mounts heavy harpoons in {primary_settlement}, mercs hired by {faction_b} gather in {secondary_settlement}. The islands are losing altitude, demanding immediate action."
                ),
                (
                    f"A rupture in primary wind currents surrounds the summit island of {primary_settlement}, rendering air travel impossible. An armed dispute between {faction_a} and {faction_b} has stranded colonies in {secondary_settlement}.",
                    f"{faction_a} captured a mythical sky-beast capable of calming gales in {primary_settlement}. {faction_b} mobilized sky-pirates to free the creature, arguing that chaining it will disrupt global jet streams and smash {secondary_settlement}'s islands together.",
                    f"Solar-sail ships collide amidst storm clouds. While {faction_a} fortifies the astral cage in {primary_settlement}, daring corsairs from {faction_b} plan an aerial boarding maneuver from the docks of {secondary_settlement}."
                ),
                (
                    f"Fragments from upper floating islands have begun crashing into residential districts of {primary_settlement}. Political deadlock between {faction_a} and {faction_b} blocked evacuations to {secondary_settlement}.",
                    f"{faction_a} proposes detonating rogue floating rocks threatening {primary_settlement} using alchemical charges. However, {faction_b} fiercely opposes this, revealing those sky-lands hold ancestral tombs sacred to {secondary_settlement}.",
                    f"Raining stone and shattered crystals pummel the abyss. As {faction_a} positions flak cannons in {primary_settlement}, activists from {faction_b} secure magic mooring lines in {secondary_settlement} to prevent structural collapse."
                ),
                (
                    f"An unstable ether portal tore open in the upper skies of {primary_settlement}, summoning electromagnetic gales. A cutthroat race to stabilize it pits {faction_a} against {faction_b}, threatening {secondary_settlement}.",
                    f"{faction_a} aims to harness the rift to open trade lanes to alien realms from {primary_settlement}. {faction_b} fights to seal it immediately, fearing void horrors will swarm {secondary_settlement}.",
                    f"Golden lightning pierces cracked firmaments. While {faction_a} gathers star-mages in {primary_settlement}, defenders from {faction_b} scribe sealing runes in {secondary_settlement} before the portal spreads irreversibly."
                )
            ],
            "5": [
                (
                    f"Beneath twin scorching suns, golden dunes surrounding the oasis of {primary_settlement} guard tombs of forgotten kings. Geopolitical tensions between {faction_a} and {faction_b} have halted spice and water caravans sustaining the outpost of {secondary_settlement}.",
                    f"Conflict flared when the Sun Pharaoh's Tomb opened in {primary_settlement}, revealing an amulet commanding sandstorms. {faction_a} plans to march on free cities, while {faction_b} seeks to bury the relic to prevent an ancient desert curse from consuming {secondary_settlement}.",
                    f"Mirages dance alongside clashing steel on hot sand. {faction_a} entrenches its legions near {primary_settlement}, while {faction_b} rallies nomads in {secondary_settlement}. A massive sandstorm approaches, threatening to entomb all life."
                ),
                (
                    f"The great subterranean aquifer beneath {primary_settlement} has begun drying rapidly. A ruthless war over life-giving water pits {faction_a} against {faction_b}, endangering all living beings in {secondary_settlement}.",
                    f"{faction_a} seized control of deep wells in {primary_settlement} to ration water in exchange for absolute obedience. {faction_b} retaliated by destroying imperial aqueducts, promising free water for {secondary_settlement}.",
                    f"Blistering sun and unbearable thirst choke the land. As {faction_a} guards the wells in {primary_settlement} with crossbows, nomads from {faction_b} launch night raids from {secondary_settlement}'s oases."
                ),
                (
                    f"Gigantic sand worms driven by primeval magic have awakened near {primary_settlement}. Disagreements on how to handle the beasts between {faction_a} and {faction_b} have isolated {secondary_settlement}.",
                    f"{faction_a} intends to poison spice fields in {primary_settlement} to exterminate the worms. {faction_b} argues the beasts are sacred and killing them will collapse underground ecosystems in {secondary_settlement}.",
                    f"The earth quakes beneath roaring behemoths. While {faction_a} prepares alchemical catapults in {primary_settlement}, shamans from {faction_b} perform ritual dances in {secondary_settlement} to redirect the worms."
                ),
                (
                    f"An eternal solar eclipse has plunged {primary_settlement} into unprecedented freezing darkness. A battle for the solar relic pits {faction_a} against {faction_b}, freezing wells in {secondary_settlement}.",
                    f"{faction_a} accuses {faction_b} of using necromancy to steal the solar spark from {primary_settlement}'s grand temple. {faction_b} proves the high priest sold it to shadow entities for immortality in {secondary_settlement}.",
                    f"Icy winds and frozen dunes disorient travelers. As {faction_a} patrols temples in {primary_settlement}, paladins from {faction_b} seek the thermal core hidden in {secondary_settlement} to restore warmth to the world."
                )
            ],
            "6": [
                (
                    f"For centuries, the realm around {primary_settlement} thrived under the influence of {theme_name}. However, an ideological rift between {faction_a} and {faction_b} has destabilized trade routes and arcane grids nourishing {secondary_settlement}.",
                    f"The dispute escalated when {faction_a} discovered a forgotten reservoir of mystical energy beneath {primary_settlement}. Attempting to monopolize it, they mobilized troops, provoking a swift response from {faction_b}, who warn that tampering with the reservoir will cause a cataclysm.",
                    f"Urban skirmishes and espionage now threaten open war. While {faction_a} fortifies {primary_settlement}, {faction_b} agents recruit adventurers in {secondary_settlement}. The energy source grows unstable, placing the realm's fate in the hands of bold champions."
                ),
                (
                    f"Bio-glass spires and floating gardens in {primary_settlement} suffer from a outbreak of glowing fungal spores. Political deadlock between {faction_a} and {faction_b} delays the cure awaited by {secondary_settlement}.",
                    f"{faction_a} plans to burn infected farming sectors in {primary_settlement} using concentrated sunlight beams. {faction_b} maintains the blight is a natural forest response and seeks to adapt {secondary_settlement}'s flora.",
                    f"Bioluminescent light flickers across giant tree canopies. As {faction_a} deploys solar fire prisms in {primary_settlement}, eco-mages from {faction_b} distribute natural antitoxins in {secondary_settlement}."
                ),
                (
                    f"A failure in the photo-arcane grid lighting {primary_settlement}'s canopy domes threatens to plunge everything into darkness. A clash over photovoltaic crystals pits {faction_a} against {faction_b}, impacting {secondary_settlement}.",
                    f"{faction_a} attempts to hoard solar generators in {primary_settlement} to power central domes exclusively. {faction_b} launched sabotage operations to restore power to peripheral settlements in {secondary_settlement}.",
                    f"Unprecedented shadows fall over the technomantic jungle. While {faction_a} guards light arrays in {primary_settlement}, botanical engineers from {faction_b} tap into mystic roots in {secondary_settlement} to ignite emergency light."
                ),
                (
                    f"The Great Mother Tree housing {primary_settlement} has begun petrifying mysteriously. The feud between {faction_a} and {faction_b} blocks access to healing sap urgently needed in {secondary_settlement}.",
                    f"{faction_a} claims synthetic catalysts saved the tree in {primary_settlement}. However, {faction_b} exposes that chemicals are accelerating petrification to harvest gemstone timber for {secondary_settlement}.",
                    f"Glass leaves and quartz branches creak in the wind. As {faction_a} protects injection pumps in {primary_settlement}, cyber-druids from {faction_b} search for pure seeds in {secondary_settlement} to plant a new core."
                )
            ],
            "7": [
                (
                    f"In fog-draped dark woods around {primary_settlement}, whispers of forbidden pacts echo through every hollow. A direct confrontation between {faction_a} and {faction_b} has shattered ancient truces protecting coven lore and {secondary_settlement}'s Ley lines.",
                    f"The crisis was sparked by unearthing the Book of Primordial Shadows in {primary_settlement}. {faction_a} seeks to summon a cosmic entity for power, while {faction_b} warns breaking the seals will unleash a demonic plague over {secondary_settlement}.",
                    f"Green flames flicker on tallow candles as ravens watch the roads. While {faction_a} prepares the grand ritual in {primary_settlement}, shadow hunters from {faction_b} gather in {secondary_settlement}. A blood moon eclipse approaches, marking the final deadline."
                ),
                (
                    f"A pit of brimstone and shadow emerged in {primary_settlement}'s plaza, attracting lesser fiends. The desperate struggle between {faction_a} and {faction_b} paralyzed magic trade with {secondary_settlement}.",
                    f"{faction_a} struck a deal with an archdevil to command fiendish legions in {primary_settlement}. {faction_b} violently opposed this, forming purification squads to cleanse pits in {secondary_settlement} before the portal opens completely.",
                    f"Brimstone stench and infernal whispers fill the night. While {faction_a} fortifies slopes in {primary_settlement}, rebel warlocks from {faction_b} gather silver amulets in {secondary_settlement} to seal the rifts."
                ),
                (
                    f"The matriarch of the ruling coven in {primary_settlement} was assassinated with a white mandrake blade. The bloody witch hunt launched between {faction_a} and {faction_b} terrifies residents of {secondary_settlement}.",
                    f"{faction_a} blames {secondary_settlement}'s warlock circle and began mass arrests in {primary_settlement}. {faction_b} asserts the matriarch was betrayed by her own acolytes to seize her pactlands.",
                    f"Dried mistletoe and bloody runes mark doorways. As {faction_a} burns huts in {primary_settlement}, renegade inquisitors from {faction_b} protect refugee sages in {secondary_settlement} while investigating the crime."
                ),
                (
                    f"A nightmarish hallucinatory fog erupted from bogs near {primary_settlement}. A violent clash over the lunar amulet pits {faction_a} against {faction_b}, threatening {secondary_settlement}.",
                    f"{faction_a} tries to weaponize the fog to subdue villages around {primary_settlement}. {faction_b} fights to synthesize an antidote using black willow roots from {secondary_settlement}.",
                    f"Ghosts and shadows dance among leafless groves. While {faction_a} patrols swamps in {primary_settlement}, herbalists from {faction_b} collect night-blooming flowers in {secondary_settlement} against the clock."
                )
            ],
            "8": [
                (
                    f"In grand crimson halls of {primary_settlement}, immortal aristocrats feast while common folk bleed. A shadowy war between {faction_a} and {faction_b} threatens the power balance with {secondary_settlement}.",
                    f"The conflict erupted over shortages of 'Pure Sanguine Elixir' stored beneath {primary_settlement}. {faction_a} seeks to restrict consumption to high nobility, while {faction_b} conspires to poison {secondary_settlement}'s wells to raise an army of thralls.",
                    f"Clinking crystal glasses and hidden duels define night life. As {faction_a} secures crypts in {primary_settlement}, {faction_b} infiltrators recruit living mercenaries in {secondary_settlement}. Night stretches on as the scent of fresh blood fills the air."
                ),
                (
                    f"A legendary vampire hunter was captured and staked in {primary_settlement}'s square. A rescue attempt by {faction_b} against {faction_a} turned the night into a bloodbath affecting {secondary_settlement}.",
                    f"{faction_a} plans to execute the hunter during a full moon in {primary_settlement} to absorb his sunlight immunity. {faction_b} aims to free him in exchange for secrets to destroy elder counts in {secondary_settlement}.",
                    f"Velvet drapes and bloodstains adorn cobblestone avenues. While {faction_a} guards battlements in {primary_settlement}, rebel hunters from {faction_b} infiltrate from {secondary_settlement} armed with ash stakes."
                ),
                (
                    f"The 'Silver Sweat' plague, lethal to trueborn vampires, spreads through {primary_settlement}'s courts. A desperate clash over alchemical medicine pits {faction_a} against {faction_b}, destabilizing {secondary_settlement}.",
                    f"{faction_a} accuses {faction_b} of engineering the plague to eradicate royalty in {primary_settlement}. {faction_b} maintains the plague is divine retribution for tyranny inflicted on mortals in {secondary_settlement}.",
                    f"Black carriages with heavy curtains cross bridges at midnight. As {faction_a} quarantines palaces in {primary_settlement}, plague doctors allied with {faction_b} hunt for patient zero in {secondary_settlement}."
                ),
                (
                    f"The Grand Conclave of Fourteen Immortal Families has convened in {primary_settlement}'s fortress. An assassination plot between {faction_a} and {faction_b} threatens county-wide war toward {secondary_settlement}.",
                    f"{faction_a} seeks to crown an absolute king to unite courts under {primary_settlement}. {faction_b} planted alchemical explosives in foundations to eradicate the bloodlines and liberate {secondary_settlement}.",
                    f"Carrier bats and night messengers fill gothic skies. While {faction_a} reinforces honor guards in {primary_settlement}, {faction_b} spies ignite fuses in catacombs beneath {secondary_settlement}."
                )
            ],
            "9": [
                (
                    f"Along prosperous trade routes centered on {primary_settlement}, caravans laden with mystic silk and arcane spices generate vast wealth. Cutthroat commercial rivalry between {faction_a} and {faction_b} has blocked mountain passes to {secondary_settlement}.",
                    f"The crisis peaked when merchants discovered legendary 'Golden Lotus Spice' near {primary_settlement}, capable of granting immortality. {faction_a} monopolized it via extortionate tariffs, while {faction_b} funds trade pirates to raid shipments bound for {secondary_settlement}.",
                    f"Exotic fabric markets, poisons, and guards crowd the bazaars. As {faction_a} fortifies caravanserai in {primary_settlement}, {faction_b} agents hire smugglers in {secondary_settlement}. With routes closed and goods rotting, the trade empire stands on the brink of collapse."
                ),
                (
                    f"A fleet of flying junks carrying dragon silk arrived at {primary_settlement}'s river port. A violent customs dispute between {faction_a} and {faction_b} ignited fires in {secondary_settlement}'s warehouses.",
                    f"{faction_a} confiscated cargo citing relic smuggling in {primary_settlement}. {faction_b} mobilized sailor unions to besiege customs towers, promising to distribute silk to struggling artisans in {secondary_settlement}.",
                    f"The smell of burning cinnamon and red silk hangs heavy. While {faction_a} deploys gold guard mercenaries in {primary_settlement}, river pirates from {faction_b} raid naval armories in {secondary_settlement}."
                ),
                (
                    f"Mass counterfeiting of imperial jade currency has bankrupted financial houses in {primary_settlement}. The relentless hunt for counterfeiters pits {faction_a} against {faction_b}, plunging {secondary_settlement} into poverty.",
                    f"{faction_a} blames alchemist guilds in {secondary_settlement} and blockaded markets in {primary_settlement}. {faction_b} proves high ministers of {faction_a} printed fake coin to finance personal wars.",
                    f"Deserted bazaars and guards demanding blood taxes mark the streets. As {faction_a} executes suspects in {primary_settlement}, accountants from {faction_b} try to recover pure jade reserves hidden in {secondary_settlement}."
                ),
                (
                    f"A new maritime spice route was discovered, shortening travel between {primary_settlement} and {secondary_settlement}. Privateering wars between {faction_a} and {faction_b} have littered the sea with burning shipwrecks.",
                    f"{faction_a} built stone forts on strait islands to tax ships from {primary_settlement}. {faction_b} equipped corsair ships with alchemical fire to destroy bulwarks and open the route to {secondary_settlement}.",
                    f"Jade sails and black flags battle among coral reefs. While {faction_a} reinforces naval cannons in {primary_settlement}, corsairs from {faction_b} recruit daring captains in {secondary_settlement}'s ports to break the blockade."
                )
            ]
        }

    theme_stories = stories.get(theme_key, stories["1"])
    chosen_story_tuple = random.choice(theme_stories)
    return " ".join(chosen_story_tuple)

# ==========================================
# UNIVERSE PDF GENERATOR
# ==========================================

def create_universe_pdf(
    universe_data: Dict[str, Any], output_path: str, is_es: bool = False
):
    """Generates game.pdf with full lore, encounters, loot, DM goodies, and generated party members."""
    labels = DATA_ES["labels"] if is_es else DATA_EN["labels"]

    theme = universe_data["theme"]
    uid = universe_data["universe_id"]
    factions = universe_data["factions"]
    settlements = universe_data["settlements"]
    conflict = universe_data["global_conflict"]
    party = universe_data["party"]
    encounters = universe_data.get("encounters", {})

    # Encounters HTML formatting
    encounters_html = ""
    if encounters:
        encounters_html = f"""
        <div class="section-title">{labels['encounters_title']}</div>
        
        <!-- STAGE 1 -->
        <div class="encounter-card stage-low">
            <div class="encounter-header">
                <span class="stage-badge badge-low">{labels['low_battle']}</span>
                <span class="location-title"><b>{labels['location']}:</b> {encounters['low']['location']}</span>
            </div>
            <table class="encounter-table">
                <tr>
                    <th>{labels['enemies']}</th>
                    <th>{labels['armour']}</th>
                    <th>{labels['goodies']}</th>
                </tr>
        """
        for e in encounters['low']['enemies']:
            encounters_html += f"""
                <tr>
                    <td><b>{e['name']}</b> ({e['type']})</td>
                    <td>{e['armour']}</td>
                    <td>{e['goodies']}</td>
                </tr>
            """
        encounters_html += "</table></div>"

        # STAGE 2
        encounters_html += f"""
        <div class="encounter-card stage-mid">
            <div class="encounter-header">
                <span class="stage-badge badge-mid">{labels['mid_battle']}</span>
                <span class="location-title"><b>{labels['location']}:</b> {encounters['mid']['location']}</span>
            </div>
            <table class="encounter-table">
                <tr>
                    <th>{labels['enemies']}</th>
                    <th>{labels['armour']}</th>
                    <th>{labels['goodies']}</th>
                </tr>
        """
        for e in encounters['mid']['enemies']:
            encounters_html += f"""
                <tr>
                    <td><b>{e['name']}</b> ({e['type']})</td>
                    <td>{e['armour']}</td>
                    <td>{e['goodies']}</td>
                </tr>
            """
        encounters_html += "</table></div>"

        # STAGE 3 (BOSS)
        encounters_html += f"""
        <div class="encounter-card stage-boss">
            <div class="encounter-header">
                <span class="stage-badge badge-boss">{labels['boss_battle']}</span>
                <span class="location-title"><b>{labels['location']}:</b> {encounters['boss']['location']}</span>
            </div>
            <table class="encounter-table">
                <tr>
                    <th>{labels['enemies']}</th>
                    <th>{labels['armour']}</th>
                    <th>{labels['goodies']}</th>
                </tr>
        """
        for e in encounters['boss']['enemies']:
            encounters_html += f"""
                <tr>
                    <td><b class="boss-name">{e['name']}</b> ({e['type']})</td>
                    <td>{e['armour']}</td>
                    <td>{e['goodies']}</td>
                </tr>
            """
        encounters_html += f"""
            </table>
            <div class="boss-unlock">
                <b>{labels['unlocks']}:</b> {encounters['boss'].get('unlocks', 'N/A')}
            </div>
        </div>
        """

    party_html = ""
    for p in party:
        party_html += f"""
        <div class="party-card">
            <div class="party-name">{p['name']}</div>
            <div class="party-sub">{p['race']} {p['class']} ({p['subclass']}) | {labels['level']} {p['level']}</div>
            <div class="party-meta"><b>{labels['background']}:</b> {p['background']} | <b>{labels['faction']}:</b> {p['faction']}</div>
            <div class="party-meta"><b>{labels['alignment']}:</b> {p['alignment']}</div>
            <div class="party-hook">"{p['hook']}"</div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{labels['game_universe']}</title>
        <style>
            @page {{
                size: A4;
                margin: 18mm 18mm 18mm 18mm;
            }}
            body {{
                font-family: 'Georgia', serif;
                color: #2b2b2b;
                line-height: 1.4;
                font-size: 10.5pt;
                background-color: #fff;
            }}
            .header {{
                text-align: center;
                border-bottom: 2.5px solid #8b0000;
                padding-bottom: 8px;
                margin-bottom: 15px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 22pt;
                color: #8b0000;
                text-transform: uppercase;
                letter-spacing: 1.5px;
            }}
            .header .subtitle {{
                font-size: 11pt;
                font-style: italic;
                color: #555;
                margin-top: 4px;
            }}
            .grid-2 {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 12px;
            }}
            .box {{
                width: 48%;
                background: #fdfbf7;
                border: 1px solid #dcd6cd;
                padding: 10px;
                border-radius: 4px;
                box-sizing: border-box;
            }}
            .box h3 {{
                margin-top: 0;
                margin-bottom: 6px;
                color: #8b0000;
                font-size: 11pt;
                border-bottom: 1px solid #e0dcd3;
                padding-bottom: 3px;
                text-transform: uppercase;
            }}
            .box ul {{
                margin: 0;
                padding-left: 18px;
            }}
            .box li {{
                margin-bottom: 4px;
            }}
            .section-title {{
                font-size: 13pt;
                color: #8b0000;
                border-bottom: 1.5px solid #8b0000;
                margin-top: 15px;
                margin-bottom: 10px;
                padding-bottom: 3px;
                text-transform: uppercase;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
            .story-box {{
                background: #fdfbf7;
                border-left: 3px solid #8b0000;
                padding: 10px 12px;
                margin-bottom: 15px;
                font-size: 10pt;
                text-align: justify;
                border-radius: 0 4px 4px 0;
            }}
            
            /* Encounter Dossier Styles */
            .encounter-card {{
                background: #faf8f5;
                border: 1px solid #d0c8b8;
                border-radius: 5px;
                padding: 8px 10px;
                margin-bottom: 10px;
            }}
            .stage-low {{ border-left: 4px solid #2e7d32; }}
            .stage-mid {{ border-left: 4px solid #d84315; }}
            .stage-boss {{ border-left: 4px solid #8b0000; background: #fdf6f6; }}
            
            .encounter-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 6px;
            }}
            .stage-badge {{
                font-size: 8.5pt;
                font-weight: bold;
                text-transform: uppercase;
                padding: 2px 6px;
                border-radius: 3px;
                color: #fff;
            }}
            .badge-low {{ background: #2e7d32; }}
            .badge-mid {{ background: #d84315; }}
            .badge-boss {{ background: #8b0000; }}
            .location-title {{
                font-size: 9.5pt;
                color: #333;
            }}
            .encounter-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 8.5pt;
                margin-top: 4px;
            }}
            .encounter-table th {{
                background: #eae5dc;
                color: #444;
                text-align: left;
                padding: 4px 6px;
                border: 1px solid #d0c8b8;
                font-size: 8pt;
                text-transform: uppercase;
            }}
            .encounter-table td {{
                padding: 4px 6px;
                border: 1px solid #e2dcce;
                vertical-align: top;
            }}
            .boss-name {{
                color: #8b0000;
            }}
            .boss-unlock {{
                margin-top: 6px;
                font-size: 8.5pt;
                color: #4a148c;
                background: #f3e5f5;
                padding: 5px 8px;
                border-radius: 3px;
                border: 1px solid #e1bee7;
            }}

            .party-grid {{
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
            }}
            .party-card {{
                width: 48%;
                background: #fdfbf7;
                border: 1px solid #dcd6cd;
                padding: 8px 10px;
                border-radius: 4px;
                margin-bottom: 10px;
                box-sizing: border-box;
            }}
            .party-name {{
                font-weight: bold;
                font-size: 11pt;
                color: #8b0000;
            }}
            .party-sub {{
                font-size: 9pt;
                font-weight: bold;
                color: #444;
                margin-bottom: 4px;
            }}
            .party-meta {{
                font-size: 8.5pt;
                color: #666;
            }}
            .party-hook {{
                font-size: 8.5pt;
                font-style: italic;
                margin-top: 4px;
                color: #333;
                border-top: 1px dashed #e0dcd3;
                padding-top: 4px;
            }}
            .footer {{
                text-align: center;
                font-size: 8pt;
                color: #888;
                margin-top: 15px;
                border-top: 1px solid #ddd;
                padding-top: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{labels['game_universe']}</h1>
            <div class="subtitle">{labels['theme']}: <b>{theme}</b> | {labels['universe_id']}: <b>{uid}</b></div>
        </div>

        <div class="grid-2">
            <div class="box">
                <h3>{labels['dominant_factions']}</h3>
                <ul>
                    {"".join([f"<li><b>{f}</b></li>" for f in factions])}
                </ul>
            </div>
            <div class="box">
                <h3>{labels['major_settlements']}</h3>
                <ul>
                    {"".join([f"<li><b>{s}</b></li>" for s in settlements])}
                </ul>
            </div>
        </div>

        <div class="section-title">{labels['global_conflict']}</div>
        <div class="story-box">
            {conflict}
        </div>

        {encounters_html}

        <div class="section-title">{labels['party_members']}</div>
        <div class="party-grid">
            {party_html}
        </div>

    </body>
    </html>
    """
    HTML(string=html_content).write_pdf(output_path)

# ==========================================
# CHARACTER SHEET PDF GENERATOR
# ==========================================

def create_character_pdf(
    char_data: Dict[str, Any], output_path: str, is_es: bool = False
):
    """Generates character page PDF following theme & layout styling."""
    labels = DATA_ES["labels"] if is_es else DATA_EN["labels"]

    stats = char_data["stats"]
    skills = DATA_ES["skills_by_attr"] if is_es else DATA_EN["skills_by_attr"]

    stats_html = ""
    for attr in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        s_val = stats[attr]["score"]
        s_mod = stats[attr]["mod"]
        attr_label = labels.get(attr.lower(), attr)
        sk_list = skills.get(attr, [])

        sk_html = ""
        if sk_list:
            sk_html = "<div class='skill-list'>" + ", ".join(sk_list) + "</div>"

        stats_html += f"""
        <div class="stat-box">
            <div class="stat-label">{attr_label} ({attr})</div>
            <div class="stat-score">{s_val}</div>
            <div class="stat-mod">{s_mod}</div>
            {sk_html}
        </div>
        """

    # Extract combat & inventory details
    combat = char_data.get("combat", {})
    hp_val = combat.get("hp", "10")
    ac_val = combat.get("ac", "10")
    init_val = combat.get("initiative", "+0")
    prof_val = combat.get("proficiency", "+2")
    equipped_armor = combat.get("equipped_armor", "None")
    main_attack = combat.get("main_attack", "None")
    starting_equipment = combat.get("starting_equipment", "None")
    magic_spells = combat.get("magic_spells", "None")

    subclass_html = ""
    if char_data["level"] >= 3:
        subclass_html = f"""
            <div class="profile-item">
                <label>{labels['subclass']}</label>
                <span>{char_data['subclass']}</span>
            </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{labels['character_sheet']} - {char_data['name']}</title>
        <style>
            @page {{
                size: A4;
                margin: 18mm;
            }}
            body {{
                font-family: 'Georgia', serif;
                color: #2b2b2b;
                line-height: 1.4;
                font-size: 10pt;
                background-color: #fff;
            }}
            .header {{
                text-align: center;
                border-bottom: 2.5px solid #8b0000;
                padding-bottom: 6px;
                margin-bottom: 12px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 20pt;
                color: #8b0000;
                text-transform: uppercase;
                letter-spacing: 1.5px;
            }}
            .char-name {{
                font-size: 16pt;
                font-weight: bold;
                color: #111;
                margin-top: 4px;
            }}
            .profile-grid {{
                display: flex;
                flex-wrap: wrap;
                background: #fdfbf7;
                border: 1px solid #dcd6cd;
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 12px;
            }}
            .profile-item {{
                width: 33.33%;
                margin-bottom: 6px;
                box-sizing: border-box;
            }}
            .profile-item.full {{
                width: 100%;
            }}
            .profile-item label {{
                font-weight: bold;
                font-size: 8.5pt;
                color: #8b0000;
                text-transform: uppercase;
                display: block;
            }}
            .profile-item span {{
                font-size: 10pt;
                color: #222;
            }}
            .section-title {{
                font-size: 11pt;
                color: #8b0000;
                border-bottom: 1.5px solid #8b0000;
                margin-top: 12px;
                margin-bottom: 8px;
                padding-bottom: 2px;
                text-transform: uppercase;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
            .desc-box {{
                background: #fdfbf7;
                border: 1px solid #dcd6cd;
                padding: 8px 10px;
                border-radius: 4px;
                margin-bottom: 10px;
                font-size: 9.5pt;
            }}
            .desc-box p {{
                margin: 0 0 4px 0;
            }}
            .desc-box p:last-child {{
                margin-bottom: 0;
            }}
            
            /* Stats Row */
            .stats-container {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 12px;
            }}
            .stat-box {{
                width: 15%;
                background: #fdfbf7;
                border: 1px solid #8b0000;
                border-radius: 5px;
                text-align: center;
                padding: 6px 2px;
                box-sizing: border-box;
            }}
            .stat-label {{
                font-size: 7.5pt;
                font-weight: bold;
                color: #8b0000;
                text-transform: uppercase;
            }}
            .stat-score {{
                font-size: 14pt;
                font-weight: bold;
                color: #111;
                margin: 2px 0;
            }}
            .stat-mod {{
                font-size: 10pt;
                font-weight: bold;
                background: #8b0000;
                color: #fff;
                border-radius: 3px;
                display: inline-block;
                padding: 1px 6px;
            }}
            .skill-list {{
                font-size: 6.5pt;
                color: #555;
                margin-top: 4px;
                border-top: 1px dashed #ccc;
                padding-top: 2px;
            }}

            /* Combat & Weaponry Statistics */
            .combat-squares {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
            }}
            .combat-square {{
                width: 23%;
                background: #fdfbf7;
                border: 1.5px solid #8b0000;
                border-radius: 8px;
                text-align: center;
                padding: 8px 4px;
                box-sizing: border-box;
            }}
            .combat-square-label {{
                font-size: 8pt;
                font-weight: bold;
                color: #8b0000;
                text-transform: uppercase;
            }}
            .combat-square-value {{
                font-size: 15pt;
                font-weight: bold;
                color: #111;
                margin-top: 4px;
            }}
            .combat-text-lines {{
                background: #fdfbf7;
                border: 1px solid #dcd6cd;
                padding: 8px 10px;
                border-radius: 4px;
                margin-bottom: 12px;
                font-size: 9.5pt;
            }}
            .combat-text-line {{
                margin-bottom: 4px;
            }}
            .combat-text-line:last-child {{
                margin-bottom: 0;
            }}

            /* Inventory and Magic */
            .inventory-magic-box {{
                background: #fdfbf7;
                border: 1px solid #dcd6cd;
                padding: 8px 10px;
                border-radius: 4px;
                margin-bottom: 12px;
                font-size: 9.5pt;
            }}
            .inv-item {{
                margin-bottom: 6px;
            }}
            .inv-item:last-child {{
                margin-bottom: 0;
            }}

            .hook-box {{
                background: #fdfbf7;
                border-left: 3px solid #8b0000;
                padding: 8px 10px;
                font-style: italic;
                font-size: 9.5pt;
                border-radius: 0 4px 4px 0;
            }}
            .footer {{
                text-align: center;
                font-size: 8pt;
                color: #888;
                margin-top: 15px;
                border-top: 1px solid #ddd;
                padding-top: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{labels['character_sheet']}</h1>
            <div class="char-name">{char_data['name']}</div>
        </div>

        <div class="profile-grid">
            <div class="profile-item">
                <label>{labels['race']}</label>
                <span>{char_data['race']}</span>
            </div>
            <div class="profile-item">
                <label>{labels['class']}</label>
                <span>{char_data['class']} ({char_data['subclass']})</span>
            </div>
            {subclass_html}
            <div class="profile-item">
                <label>{labels['level']}</label>
                <span>{char_data['level']}</span>
            </div>
            <div class="profile-item">
                <label>{labels['background']}</label>
                <span>{char_data['background']}</span>
            </div>
            <div class="profile-item">
                <label>{labels['faction']}</label>
                <span>{char_data['faction']}</span>
            </div>
            <div class="profile-item">
                <label>{labels['alignment']}</label>
                <span>{char_data['alignment']}</span>
            </div>
        </div>

        <div class="section-title">{labels['identity_overview']}</div>
        <div class="desc-box">
            <p><b>{labels['race']} ({char_data['race']}):</b> {char_data['race_desc']}</p>
            <p><b>{labels['class']} ({char_data['class']} - {char_data['subclass']}):</b> {char_data['class_desc']} {char_data['subclass_desc']}</p>
            <p><b>{labels['background']} ({char_data['background']}):</b> {char_data['bg_desc']}</p>
            <p><b>{labels['alignment']} ({char_data['alignment']}):</b> {char_data['alignment_desc']}</p>
        </div>

        <div class="section-title">{labels['attributes']}</div>
        <div class="stats-container">
            {stats_html}
        </div>

        <div class="section-title">{labels['combat_title']}</div>
        <div class="combat-squares">
            <div class="combat-square">
                <div class="combat-square-label">{labels['hp']}</div>
                <div class="combat-square-value">{hp_val}</div>
            </div>
            <div class="combat-square">
                <div class="combat-square-label">{labels['ac']}</div>
                <div class="combat-square-value">{ac_val}</div>
            </div>
            <div class="combat-square">
                <div class="combat-square-label">{labels['initiative']}</div>
                <div class="combat-square-value">{init_val}</div>
            </div>
            <div class="combat-square">
                <div class="combat-square-label">{labels['proficiency']}</div>
                <div class="combat-square-value">{prof_val}</div>
            </div>
        </div>
        <div class="combat-text-lines">
            <div class="combat-text-line"><b>{labels['equipped_armor']}:</b> {equipped_armor}</div>
            <div class="combat-text-line"><b>{labels['main_attack']}:</b> {main_attack}</div>
        </div>

        <div class="section-title">{labels['inventory_magic_title']}</div>
        <div class="inventory-magic-box">
            <div class="inv-item"><b>{labels['starting_equipment']}:</b> {starting_equipment}</div>
            <div class="inv-item"><b>{labels['magic_spells']}:</b> {magic_spells}</div>
        </div>

        <div class="section-title">{labels['backstory_hook']}</div>
        <div class="hook-box">
            "{char_data['hook']}"
        </div>

    </body>
    </html>
    """
    HTML(string=html_content).write_pdf(output_path)

# ==========================================
# PROCEDURAL GENERATOR ENGINE
# ==========================================

def generate_procedural_universe(
    theme_choice: str, num_players: int, lang_choice: str, character_level: int
):
    """Main execution workflow creating folder, game.pdf, and player character sheets."""
    is_es = lang_choice == "2"
    lang_data = DATA_ES if is_es else DATA_EN

    # Resolve Theme
    themes = lang_data["themes"]
    chosen_theme_name = themes.get(theme_choice, themes["1"])

    # Create Game Directory
    game_folder = get_next_game_folder()
    os.makedirs(game_folder, exist_ok=True)
    print(f"\n[+] Created Output Directory: {game_folder}/")

    # Generate Factions
    factions = []
    for _ in range(3):
        f_type = random.choice(lang_data["faction_types"])
        adj1 = random.choice(lang_data["faction_adjectives_1"])
        adj2 = random.choice(lang_data["faction_adjectives_2"])
        if is_es:
            factions.append(f"{f_type} {adj1} {adj2}")
        else:
            factions.append(f"The {adj1} {adj2} {f_type}")

    # Generate Settlements
    settlements = random.sample(lang_data["settlements"][chosen_theme_name], 3)

    # Generate Extended Campaign Narrative Story
    conflict = generate_extended_story(
        theme_key=theme_choice,
        theme_name=chosen_theme_name,
        faction_a=factions[0],
        faction_b=factions[1],
        primary_settlement=settlements[0],
        secondary_settlement=settlements[1],
        is_es=is_es
    )

    # Generate Encounters & Threat Dossier
    encounters = generate_encounters(chosen_theme_name, lang_data)

    # Generate Characters
    name_pool = random.sample(
        lang_data["character_names"][chosen_theme_name],
        min(num_players, len(lang_data["character_names"][chosen_theme_name])),
    )

    # If requested players exceed unique name pool, supplement with defaults
    while len(name_pool) < num_players:
        name_pool.append(f"Adventurer {len(name_pool) + 1}")

    party_members = []
    character_files = []

    for i in range(num_players):
        char_name = name_pool[i]
        race = random.choice(lang_data["races"])
        cls = random.choice(lang_data["classes"])
        subclass = random.choice(lang_data["subclasses"][cls])
        bg = random.choice(lang_data["backgrounds"])
        faction = random.choice(factions)
        settlement = random.choice(settlements)
        alignment = random.choice(lang_data["alignments"])
        hook_template = random.choice(lang_data["hooks"])
        hook = hook_template.format(faction=faction, settlement=settlement)

        stats = generate_stats()
        combat_and_inv = generate_character_combat_and_inventory(cls, subclass, race, bg, stats, is_es)

        char_info = {
            "name": char_name,
            "race": race,
            "class": cls,
            "subclass": subclass,
            "level": character_level,
            "background": bg,
            "faction": faction,
            "alignment": alignment,
            "hook": hook,
            "stats": stats,
            "combat": combat_and_inv,
            "race_desc": lang_data["race_descriptions"][race],
            "class_desc": lang_data["class_descriptions"][cls],
            "subclass_desc": lang_data["subclass_descriptions"][subclass],
            "bg_desc": lang_data["background_descriptions"][bg],
            "alignment_desc": lang_data["alignment_descriptions"][alignment],
        }

        party_members.append(char_info)

        # Output individual character sheet PDF
        char_pdf_path = os.path.join(game_folder, f"character{i+1}.pdf")
        create_character_pdf(char_info, char_pdf_path, is_es=is_es)
        character_files.append(f"character{i+1}.pdf")

    # Assemble Universe Master Data
    universe_id = f"UNI-{random.randint(1000, 9999)}"
    universe_data = {
        "universe_id": universe_id,
        "theme": chosen_theme_name,
        "factions": factions,
        "settlements": settlements,
        "global_conflict": conflict,
        "encounters": encounters,
        "party": party_members,
    }

    # Generate game.pdf
    game_pdf_path = os.path.join(game_folder, "game.pdf")
    create_universe_pdf(universe_data, game_pdf_path, is_es=is_es)

    print(f"[+] World Manual Generated: {game_folder}/game.pdf")
    for cf in character_files:
        print(f"[+] Player Sheet Generated: {game_folder}/{cf}")
    print(f"[✓] Universe Generation Completed Successfully!\n")

# ==========================================
# INTERACTIVE TERMINAL PROMPT
# ==========================================

def main():
    print("==================================================")
    print("   D&D PROCEDURAL UNIVERSE GENERATOR ENGINE       ")
    print("==================================================")
    print("Select Language / Seleccione el Idioma:")
    print("1) English")
    print("2) Español")
    lang_choice = input("Choice [1-2] (Default 1): ").strip()
    if lang_choice not in ["1", "2"]:
        lang_choice = "1"

    is_es = lang_choice == "2"
    themes = DATA_ES["themes"] if is_es else DATA_EN["themes"]

    print("\nSelect World Theme / Seleccione el Tema del Mundo:")
    for k, v in themes.items():
        print(f"{k}) {v}")

    theme_choice = input("Theme Choice [1-9] (Default 1): ").strip()
    if theme_choice not in themes:
        theme_choice = "1"

    num_players_input = input(
        "Enter Number of Player Characters [1-6] (Default 4): "
    ).strip()
    try:
        num_players = int(num_players_input)
        if num_players < 1 or num_players > 8:
            num_players = 4
    except ValueError:
        num_players = 4

    character_level_input = input(
        "Enter Character Level [1+] (Default 1): "
    ).strip()
    try:
        character_level = int(character_level_input)
        if character_level < 1:
            character_level = 1
    except ValueError:
        character_level = 1

    print("\n[Engine] Synthesizing procedural world, lore chronicle, encounters, and character sheets...")
    generate_procedural_universe(theme_choice, num_players, lang_choice, character_level)

if __name__ == "__main__":
    main()