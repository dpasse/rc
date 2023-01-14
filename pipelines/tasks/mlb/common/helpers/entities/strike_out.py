from typing import Dict, Any, List, Callable, Tuple
from .utils import split_text, create_player_observation


def handle_strike_outs(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation = create_player_observation(
        player=groups[0],
        event_type=groups[1],
        extras=extras[1:],
        outs=1
    )

    observation['effort'] = extras[0]

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) (struck out) (.+)', handle_strike_outs),
]
