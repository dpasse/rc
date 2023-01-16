from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, create_player_observation, handle_extras


# pylint: disable=R0801

def handle_steals(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'type': groups[1],
    }

    observation.update(
        handle_extras(split_text(groups[0]))
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+? (caught stealing) .+)', handle_steals),
    (r'^(.+? (stole) .+)', handle_steals),
]
