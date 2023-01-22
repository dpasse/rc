from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, create_player_observation


def handle_multiple_outs(groups: List[str]) -> Dict[str, Any]:
    observation = create_player_observation(
        player=groups[0],
        event_type=groups[1],
        extras=split_text(groups[2]),
        outs=1
    )

    outs = sum(1 for move in observation['moves'] if move['type'] == 'out')
    if outs == 2 and 'double play' in observation['type']:
        observation['outs'] = 0

    if outs == 3 and 'triple play' in observation['type']:
        observation['outs'] = 0

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) ((?:ground|lin|fli|(?:bunt )?popp|sacrific)ed into (?:double|triple) play)(.+)', handle_multiple_outs),
]
