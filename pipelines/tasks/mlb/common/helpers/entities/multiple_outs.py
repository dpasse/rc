from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, handle_extras


def handle_multiple_outs(groups: List[str]) -> Dict[str, Any]:
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': groups[1],
        'outs': 1,
    }

    observation.update(
        handle_extras(split_text(groups[2]))
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) ((?:ground|lin|fli|popp)ed into (?:double|triple) play)(.+)', handle_multiple_outs),
]
