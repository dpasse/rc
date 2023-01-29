from typing import Any, Dict
import re

from .helpers import create_find_match_request, grab, FindMatch


def handle_match(match: re.Match[str]) -> Dict[str, Any]:
    return {
        'type': grab(match, 0)
    }

def handle_wild_pitch() -> FindMatch:
    expressions = [
        r'^ *(wild pitch)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)

def handle_passed_ball() -> FindMatch:
    expressions = [
        r'^ *(passed ball)'
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)
