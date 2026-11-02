"""The fixed encounter dossier of each theme.

It holds IDs into the locale files.

Originally extracted from the tables of the first, single-file
version of the generator (see the git history). It is now
hand-maintained: edit it directly.
"""

from collections.abc import Mapping
from typing import Final

from dnd_worldgen.models import Encounter, EncounterSet, EncounterStage

ENCOUNTERS_BY_THEME: Final[Mapping[str, EncounterSet]] = {
    "steampunk": EncounterSet(
        low=Encounter(
            EncounterStage.LOW,
            "abandoned_gear_sluice_substation",
            (
                "clockwork_scrapper",
                "grease_monkey_enforcer",
            ),
        ),
        mid=Encounter(
            EncounterStage.MID,
            "pneumatic_freight_station_alpha",
            (
                "steam_rig_heavy_sentry",
                "aether_tech_saboteur",
            ),
        ),
        boss=Encounter(
            EncounterStage.BOSS,
            "the_grand_over_boiler_citadel",
            ("grand_archon_vane_the_steam_forged",),
            unlock_id="steampunk_boss_unlock",
        ),
    ),
    "post_apocalyptic": EncounterSet(
        low=Encounter(
            EncounterStage.LOW,
            "irradiated_ruins_outpost",
            (
                "mutated_scavenger",
                "dust_spitter_hound",
            ),
        ),
        mid=Encounter(
            EncounterStage.MID,
            "collapsed_mana_reactor_trench",
            (
                "arcane_warped_marauder",
                "void_gazer_cultist",
            ),
        ),
        boss=Encounter(
            EncounterStage.BOSS,
            "the_scorched_void_vault",
            ("abomination_lord_malakor",),
            unlock_id="post_apocalyptic_boss_unlock",
        ),
    ),
    "sunless_ocean": EncounterSet(
        low=Encounter(
            EncounterStage.LOW,
            "rotting_barnacle_wharf",
            (
                "drowned_deckhand",
                "brine_cult_initiate",
            ),
        ),
        mid=Encounter(
            EncounterStage.MID,
            "submerged_cathedral_reef",
            (
                "abyssal_deep_diver",
                "siren_siren_born_spellweaver",
            ),
        ),
        boss=Encounter(
            EncounterStage.BOSS,
            "the_sunless_trench_sanctum",
            ("leviathan_priestess_isolda",),
            unlock_id="sunless_ocean_boss_unlock",
        ),
    ),
    "floating_isles": EncounterSet(
        low=Encounter(
            EncounterStage.LOW,
            "perilous_wind_bridge_outpost",
            (
                "sky_pirate_corsair",
                "gale_wing_raptor",
            ),
        ),
        mid=Encounter(
            EncounterStage.MID,
            "shattered_astral_dockyard",
            (
                "ether_sail_captain",
                "zephyr_elemental_construct",
            ),
        ),
        boss=Encounter(
            EncounterStage.BOSS,
            "the_apex_gravity_core_engine",
            ("sky_lord_vance_the_stormbringer",),
            unlock_id="floating_isles_boss_unlock",
        ),
    ),
    "sun_desert": EncounterSet(
        low=Encounter(
            EncounterStage.LOW,
            "sun_bleached_dune_oasis",
            (
                "sand_raider_nomad",
                "giant_dune_scorpion",
            ),
        ),
        mid=Encounter(
            EncounterStage.MID,
            "buried_tomb_entrance",
            (
                "sun_cult_zealot",
                "tomb_sentinel_construct",
            ),
        ),
        boss=Encounter(
            EncounterStage.BOSS,
            "the_solar_pharaohs_sanctum",
            ("pharaoh_kharon_the_eternal",),
            unlock_id="sun_desert_boss_unlock",
        ),
    ),
    "solarpunk": EncounterSet(
        low=Encounter(
            EncounterStage.LOW,
            "overgrown_photonic_nursery",
            (
                "wild_flora_drone",
                "rebel_eco_poacher",
            ),
        ),
        mid=Encounter(
            EncounterStage.MID,
            "bio_glass_prism_observatory",
            (
                "corrupted_photonic_weaver",
                "chitin_vine_abomination",
            ),
        ),
        boss=Encounter(
            EncounterStage.BOSS,
            "the_heart_of_the_mother_tree",
            ("arch_biomancer_helios",),
            unlock_id="solarpunk_boss_unlock",
        ),
    ),
    "pactlands": EncounterSet(
        low=Encounter(
            EncounterStage.LOW,
            "fog_shrouded_bramble_hollow",
            (
                "bog_hag_acolyte",
                "imp_familiar",
            ),
        ),
        mid=Encounter(
            EncounterStage.MID,
            "blackthorn_ritual_circle",
            (
                "pact_bound_warlock",
                "bramble_shadow_beast",
            ),
        ),
        boss=Encounter(
            EncounterStage.BOSS,
            "the_blood_moon_covenstead_altar",
            ("matriarch_morrigan_the_hex_weaver",),
            unlock_id="pactlands_boss_unlock",
        ),
    ),
    "vampire_courts": EncounterSet(
        low=Encounter(
            EncounterStage.LOW,
            "cobblestone_crypt_entrance",
            (
                "rival_blood_thrall_guard",
                "feral_vampire_bat_swarm",
            ),
        ),
        mid=Encounter(
            EncounterStage.MID,
            "scarlet_hold_ballroom",
            (
                "rival_clan_vampire_fencer",
                "sanguine_blood_mage",
            ),
        ),
        boss=Encounter(
            EncounterStage.BOSS,
            "the_grand_crimson_crypt_spire",
            ("count_vladislaus_the_blood_sovereign",),
            unlock_id="vampire_courts_boss_unlock",
        ),
    ),
    "silk_route": EncounterSet(
        low=Encounter(
            EncounterStage.LOW,
            "ambushed_spice_route_oasis",
            (
                "caravan_bandit",
                "trained_attack_falcon",
            ),
        ),
        mid=Encounter(
            EncounterStage.MID,
            "fortified_silk_warehouse",
            (
                "mercenary_guild_enforcer",
                "alchemical_spice_thrower",
            ),
        ),
        boss=Encounter(
            EncounterStage.BOSS,
            "the_golden_lotus_pagoda_fortress",
            ("spice_lord_zhao_the_golden",),
            unlock_id="silk_route_boss_unlock",
        ),
    ),
}
