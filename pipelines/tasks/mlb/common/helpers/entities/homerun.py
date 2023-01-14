import re
from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, handle_extras


def handle_homerun(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(
        re.sub(r'\([^)]+\)', '', groups[2]), ## (565 feet)
    )

    observation = {
        'player': groups[0],
        'type': groups[1],
        'at': extras[0],
        'runs': 1,
    }

    observation.update(
        handle_extras(extras[1:])
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) ((?:homer)ed) to (.+)', handle_homerun),
]
