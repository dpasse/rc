from typing import Dict, Any, List, Callable, Tuple
from .utils import split_text, handle_extras


def handle_strike_outs(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])

    observation = {
        'player': groups[0],
        'type': groups[1],
        'effort': extras[0],
        'outs': 1,
    }

    observation.update(
        handle_extras(extras[1:])
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) (struck out) (.+)', handle_strike_outs),
]
