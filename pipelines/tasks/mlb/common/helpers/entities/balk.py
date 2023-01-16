from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, handle_extras


def handle_balk(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'type': 'balk',
    }

    observation.update(
        handle_extras(split_text(groups[0]))
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+? (?:balk).+)', handle_balk),
]
