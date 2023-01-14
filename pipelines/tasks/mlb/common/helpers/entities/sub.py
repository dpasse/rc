from typing import Dict, Any, List, Tuple, Callable
from .utils import clean_text


def handle_sub(groups: List[str]) -> Dict[str, Any]:
    is_pitch = clean_text(groups[1]).startswith('pitch')
    return {
        'player': groups[0],
        'type': 'sub-p' if is_pitch else 'sub-f',
    }

exports: List[Tuple[str, Callable[[List[str]], Dict[str, Any]]]] = [
    (r'^(.+?) ((?:hit|ran) for|in\b|a[st]\b|catching|pitch(?:ing|es to))', handle_sub),
]
