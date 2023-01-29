from typing import Any, Dict
import re

from .helpers import grab, create_find_match_request, FindMatch


def handle_match(match: re.Match[str]) -> Dict[str, Any]:
    return {
        'type': grab(match, 1),
        'at': grab(match, 2),
    }

def handle_steal() -> FindMatch:
    expressions = [
        r'^ *.+? (steals) (.+)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)

def handle_caught_stealing() -> FindMatch:
    expressions = [
        r'^ *.+? (caught stealing) (.+)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)
