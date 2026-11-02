"""Theme IDs and the settlements each theme contains.

Originally extracted from the tables of the first, single-file
version of the generator (see the git history). It is now
hand-maintained: edit it directly.
"""

from collections.abc import Mapping
from typing import Final

#: Theme IDs in menu order: menu choice N selects ``THEME_IDS[N - 1]``.
THEME_IDS: Final[tuple[str, ...]] = (
    "steampunk",
    "post_apocalyptic",
    "sunless_ocean",
    "floating_isles",
    "sun_desert",
    "solarpunk",
    "pactlands",
    "vampire_courts",
    "silk_route",
)

DEFAULT_THEME_ID: Final = THEME_IDS[0]

SETTLEMENT_IDS_BY_THEME: Final[Mapping[str, tuple[str, ...]]] = {
    "steampunk": (
        "cogford",
        "brassridge",
        "aether_spire",
        "iron_haven",
        "steam_gallow",
    ),
    "post_apocalyptic": (
        "ash_home",
        "rift_edge",
        "scrap_spire",
        "bone_hollow",
        "cinder_glow",
    ),
    "sunless_ocean": (
        "black_tide",
        "drown_port",
        "mire_gallow",
        "gloom_bay",
        "abyssal_rest",
    ),
    "floating_isles": (
        "sky_reach",
        "cloud_apex",
        "wind_grip",
        "aerie",
        "zephyr_rest",
    ),
    "sun_desert": (
        "sun_gate",
        "oasis_prime",
        "silt_reach",
        "dune_wall",
        "scorpion_rift",
    ),
    "solarpunk": (
        "sol_habitat",
        "aethel_flora",
        "bio_glass_spire",
        "verdant_sanctuary",
        "prism_glow",
    ),
    "pactlands": (
        "whisper_hollow",
        "bramble_coven",
        "blackthorn_spire",
        "eldritch_fen",
        "moon_gallows",
    ),
    "vampire_courts": (
        "castle_sanguine",
        "crimson_spire",
        "blood_gallow",
        "scarlet_hold",
        "vein_reach",
    ),
    "silk_route": (
        "jade_haven",
        "golden_silk_spire",
        "lotus_port",
        "spice_gallow",
        "emerald_reach",
    ),
}


def require_theme(theme_id: str) -> str:
    """Return ``theme_id`` if it is known, else raise ValueError.

    The error lists the valid theme IDs.
    """
    if theme_id not in THEME_IDS:
        known = ", ".join(THEME_IDS)
        raise ValueError(
            f"Unknown theme ID {theme_id!r}. Known themes: {known}"
        )
    return theme_id
