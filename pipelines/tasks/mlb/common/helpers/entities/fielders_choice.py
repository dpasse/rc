from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, handle_extras


def handle_fielders_choice(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])

    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0]
    }

    observation.update(
        handle_extras(extras[1:])
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]]  = [
    (r'^(.+?) ((?:ground|lin|fli)ed into fielder\'s choice) to (.+)', handle_fielders_choice),
]
