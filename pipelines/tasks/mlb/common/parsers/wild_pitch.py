import re

from .helpers import create_find_match_request, grab
from .typing import ParseType, HandleType


def handle_match(match: re.Match[str]) -> HandleType:
    return {
        'type': grab(match, 0)
    }

def parse_wild_pitch() -> ParseType:
    expressions = [
        r'^ *(wild pitch)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_passed_ball() -> ParseType:
    expressions = [
        r'^ *(passed ball)'
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse
