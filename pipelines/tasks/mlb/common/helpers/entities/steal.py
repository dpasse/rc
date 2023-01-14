from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, create_player_observation


def handle_steals(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    return create_player_observation(
        player=groups[0],
        event_type=groups[1],
        at=extras[0],
        extras=extras[1:]
    )

def handle_caught_stealing(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    return create_player_observation(
        player=groups[0],
        event_type=groups[1],
        at=extras[0],
        outs=1,
        extras=extras[1:]
    )

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) (caught stealing) (.+)', handle_caught_stealing),
    (r'^(.+?) (stole) (.+)', handle_steals),
]
