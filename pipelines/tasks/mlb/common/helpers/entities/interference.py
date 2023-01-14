from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, create_player_observation

def handle_catcher_interference(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    return create_player_observation(
        player=groups[0],
        event_type=extras[0],
        at=groups[1],
        extras=extras[1:]
    )

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) reached (.+?)(?: |base)+on (catcher\'s interference.+)', handle_catcher_interference),
]
