from typing import Dict, Any, List, Callable, Tuple
from .utils import split_text, handle_extras


def handle_sacrifice(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0],
        'outs': 1,
    }

    observation.update(
        handle_extras(extras[1:])
    )

    return observation

def handle_attempted_sacrifice(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1]
    }

    observation.update(
        handle_extras(split_text(groups[2]))
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) (sacrificed),(.+)', handle_attempted_sacrifice),
    (r'^(.+?)(?: |hit)+(sacrifice fly|sacrificed) to (.+)', handle_sacrifice),
]
