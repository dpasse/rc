from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, handle_extras


def handle_balk(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'type': 'balk',
    }

    extras = split_text(groups[0])
    observation.update(
        handle_extras(extras)
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+? (?:balk).+)', handle_balk),
]
