from typing import Any, Dict
import re

from .helpers import create_find_match_request, FindMatch


def handle_match(_: re.Match[str]) -> Dict[str, Any]:
    return {
        'type': 'Error',
    }

def handle_error() -> FindMatch:
    expressions = [
        r'^ *reached on (e\d+)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)
