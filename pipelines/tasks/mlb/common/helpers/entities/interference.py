from typing import Dict, Any, List, Tuple, Callable
from .utils import split_text, handle_extras

def handle_catcher_interference(groups: List[str]) -> Dict[str, Any]:
    extras = split_text(groups[2])
    observation: Dict[str, Any] = {
        'player': groups[0],
        'type': extras[0],
        'at': groups[1],
    }

    observation.update(
        handle_extras(extras[1:])
    )

    return observation

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) reached (.+?)(?: |base)+on (catcher\'s interference.+)', handle_catcher_interference),
]
