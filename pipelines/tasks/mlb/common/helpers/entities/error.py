from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, handle_extras


def handle_error(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'type': groups[1],
    }

    observation.update(
        handle_extras(split_text(groups[0]))
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'(.+on ((?:fielding|throwing) error).+)', handle_error),
    (r'(.+on (error).+)', handle_error),
]
