from typing import Any, Callable, Dict, List, Tuple
from .utils import split_text, create_player_observation


def handle_in_play(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    return create_player_observation(
        player=groups[0],
        event_type=groups[1],
        at=extras[0],
        extras=extras[1:]
    )

def handle_in_play_out(groups: List[str]) -> Dict[str, Any]:
    observation = {
        'outs': 1,
    }

    observation.update(
        handle_in_play(groups)
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) ((?:singl|doubl|tripl)e[ds]) to (.+)', handle_in_play),
    (r'^(.+?) reached on ((?:infield|bunt) single) to (.+)', handle_in_play),
    (r'^(.+?) hit a (ground rule double) to (.+)', handle_in_play),
    (r'^(.+?)(?: |bunt)+((?:lin|ground|fli|foul|popp)ed out) to (.+)', handle_in_play_out),
]
