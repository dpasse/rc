from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, create_player_observation


def handle_walk(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[1])
    return create_player_observation(
        player=groups[0],
        event_type=extras[0],
        at='first',
        extras=extras[1:]
    )

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) ((?:(?:intentionally |)walked|hit by pitch).*)', handle_walk),
]
