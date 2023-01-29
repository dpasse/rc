from typing import Any, Dict
import re

from .helpers import grab, create_find_match_request, FindMatch


def handle_match(match: re.Match[str]) -> Dict[str, Any]:
    return {
        'type': grab(match, 1),
        'effort': grab(match, 2)
    }

def handle_strikeout() -> FindMatch:
    expressions = [
        r'^ *(strikeout) (swinging|looking)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)
