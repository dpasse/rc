import re

from .helpers import create_find_match_request, grab
from .typing import ParseType, HandleType


def handle_advance_match(match: re.Match[str]) -> HandleType:
    return {
        'player': grab(match, 1),
        'type': 'Advanced',
        'at': grab(match, 2),
    }

def parse_advance() -> ParseType:
    expressions = [
        r'^ *(.+?) to ([123]B) *$',
    ]

    return create_find_match_request(expressions, handle_advance_match, re.IGNORECASE).parse

def handle_out_advance_match(match: re.Match[str]) -> HandleType:
    return {
        'type': grab(match, 1),
    }

def parse_out_advance() -> ParseType:
    expressions = [
        r'^ *baserunner (out advancing) *$',
    ]

    return create_find_match_request(expressions, handle_out_advance_match, re.IGNORECASE).parse
