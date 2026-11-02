"""Choice of the campaign's opening story."""

import random
from collections.abc import Sequence

from dnd_worldgen.models import Faction, Story
from dnd_worldgen.rules.stories import STORY_IDS_BY_THEME
from dnd_worldgen.rules.themes import require_theme


def generate_story(
    rng: random.Random,
    theme_id: str,
    factions: Sequence[Faction],
    settlement_ids: Sequence[str],
) -> Story:
    """Pick one of the theme's stories (one random draw).

    Like the original, the first two factions are the rivals and the
    first two settlements are where the story takes place. The text is
    not built here: see :func:`dnd_worldgen.i18n.display.story_text`.
    """
    require_theme(theme_id)
    if len(factions) < 2:
        raise ValueError("A story needs at least two factions")
    if len(settlement_ids) < 2:
        raise ValueError("A story needs at least two settlements")
    return Story(
        template_id=rng.choice(STORY_IDS_BY_THEME[theme_id]),
        faction_a=factions[0],
        faction_b=factions[1],
        primary_settlement_id=settlement_ids[0],
        secondary_settlement_id=settlement_ids[1],
    )
