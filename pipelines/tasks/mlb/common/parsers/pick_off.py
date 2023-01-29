from typing import Any, Dict
import re

from .helpers import grab, create_find_match_request, FindMatch


def handle_match(match: re.Match[str]) -> Dict[str, Any]:
    return {
        'type': grab(match, 1),
    }

def handle_pick_off() -> FindMatch:
    expressions = [
        r'^ *.+? (picked off)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)
