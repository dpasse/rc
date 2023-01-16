import re
from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, create_player_observation


def handle_wild_pitch(groups) -> Dict[str, Any]:
    pitcher_match_expressions = [
        r'(?:wild pitch|passed ball) by (.+?)[,.]',
        r'on (.+?) wild pitch',
    ]

    text = groups[0]
    player = None
    for pitcher_match_expression in pitcher_match_expressions:
        pitcher_match = re.search(pitcher_match_expression, text)
        if pitcher_match:
            player = pitcher_match.group(1)
            break

    extras = split_text(text)
    observation = create_player_observation(
        player=player,
        event_type=groups[1],
        extras=extras,
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+? (wild pitch|passed ball).+)', handle_wild_pitch),
]
