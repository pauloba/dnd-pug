"""Story IDs per theme (the text is in the locale files).

Originally extracted from the tables of the first, single-file
version of the generator (see the git history). It is now
hand-maintained: edit it directly.
"""

from collections.abc import Mapping
from typing import Final

#: ``stories.<theme_id>.<story_id>`` in a locale file is a list of
#: paragraphs.
STORY_IDS_BY_THEME: Final[Mapping[str, tuple[str, ...]]] = {
    "steampunk": (
        "story_1",
        "story_2",
        "story_3",
        "story_4",
    ),
    "post_apocalyptic": (
        "story_1",
        "story_2",
        "story_3",
        "story_4",
    ),
    "sunless_ocean": (
        "story_1",
        "story_2",
        "story_3",
        "story_4",
    ),
    "floating_isles": (
        "story_1",
        "story_2",
        "story_3",
        "story_4",
    ),
    "sun_desert": (
        "story_1",
        "story_2",
        "story_3",
        "story_4",
    ),
    "solarpunk": (
        "story_1",
        "story_2",
        "story_3",
        "story_4",
    ),
    "pactlands": (
        "story_1",
        "story_2",
        "story_3",
        "story_4",
    ),
    "vampire_courts": (
        "story_1",
        "story_2",
        "story_3",
        "story_4",
    ),
    "silk_route": (
        "story_1",
        "story_2",
        "story_3",
        "story_4",
    ),
}
