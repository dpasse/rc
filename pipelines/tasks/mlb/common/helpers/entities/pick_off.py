from typing import Dict, Any, List, Tuple, Callable
from .utils import create_player_observation

def handle_pick_off(groups: List[str]) -> Dict[str, Any]:
    return create_player_observation(
        player=groups[0],
        event_type=groups[1],
        at= groups[2] if len(groups) > 2 else None,
        outs=1
    )

def handle_pick_off_error(groups: List[str]) -> Dict[str, Any]:
    observation = create_player_observation(
        player=groups[0],
        event_type=groups[2],
        at=groups[1]
    )

    observation['by'] = groups[3]

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) to (.+?) on (pickoff error) by (?:pitcher|catcher|(?:first|second|third) baseman) (.+)', handle_pick_off_error),
    (r'^(.+?) (picked off)(?: and caught stealing|) (.+)', handle_pick_off),
]
