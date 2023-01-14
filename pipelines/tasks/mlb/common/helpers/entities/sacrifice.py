from typing import Dict, Any, List, Callable, Tuple
from .utils import split_text, create_player_observation


def handle_sacrifice(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation = create_player_observation(
        player=groups[0],
        event_type=groups[1],
        at=extras[0],
        extras=extras[1:],
        outs=1
    )

    return observation

def handle_attempted_sacrifice(groups: List[str]) -> Dict[str, Any]:
    return create_player_observation(
        player=groups[0],
        event_type=groups[1],
        extras=split_text(groups[2])
    )


exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) (sacrificed),(.+)', handle_attempted_sacrifice),
    (r'^(.+?)(?: |hit)+(sacrifice fly|sacrificed) to (.+)', handle_sacrifice),
]
