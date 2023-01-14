from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, create_player_observation


def handle_multiple_outs(groups: List[str]) -> Dict[str, Any]:
    return create_player_observation(
        player=groups[0],
        event_type=groups[1],
        extras=split_text(groups[2]),
        outs=1
    )

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) ((?:ground|lin|fli|popp)ed into (?:double|triple) play)(.+)', handle_multiple_outs),
]
