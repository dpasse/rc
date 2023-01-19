import re
from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, create_player_observation


def handle_wild_pitch(groups) -> Dict[str, Any]:
    text = groups[0]

    player = 'not found'
    for pitcher_match_expression in [
        r'(?:wild pitch|passed ball) by (.+?)[,.]',
        r'on (.+?) wild pitch',
    ]:
        pitcher_match = re.search(pitcher_match_expression, text)
        if pitcher_match:
            player = pitcher_match.group(1)
            break

    observation = create_player_observation(
        player=player,
        event_type=groups[1],
        extras=split_text(text),
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+? (wild pitch|passed ball).+)', handle_wild_pitch),
]
