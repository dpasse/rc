from typing import Any, Dict
import re

from .helpers import grab, create_find_match_request, FindMatch


def handle_advance_match(match: re.Match[str]) -> Dict[str, Any]:
    return {
        'player': grab(match, 1),
        'type': 'Advanced',
        'at': grab(match, 2),
    }

def handle_advance() -> FindMatch:
    expressions = [
        r'^ *(.+?) to ([123]B) *$',
    ]

    return create_find_match_request(expressions, handle_advance_match, re.IGNORECASE)

def handle_out_advance_match(match: re.Match[str]) -> Dict[str, Any]:
    return {
        'type': grab(match, 1),
    }

def handle_out_advance() -> FindMatch:
    expressions = [
        r'^ *baserunner (out advancing) *$',
    ]

    return create_find_match_request(expressions, handle_out_advance_match, re.IGNORECASE)
