import re
from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, handle_extras, create_player_observation, search


def handle_homerun(groups: List[str]) -> Dict[str, Any]:
    distance = search(['\((\d+)'], groups[2])

    extras = split_text(
        re.sub(r'\([^)]+\)', '', groups[2]), ## (565 feet)
    )

    observation = create_player_observation(
        player=groups[0],
        event_type=groups[1],
        at=extras[0],
        extras=extras[1:],
        runs=1,
    )

    if distance:
        observation['distance'] = int(distance.group(1))

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) ((?:homer)ed) to (.+)', handle_homerun),
]
