import re

from .helpers import create_find_match_request, grab
from .typing import ParseType, HandleType


def handle_match(match: re.Match[str]) -> HandleType:
    return {
        'type': grab(match, 1),
        'effort': grab(match, 2)
    }

def parse_strikeout() -> ParseType:
    expressions = [
        r'^ *(strikeout) (swinging|looking)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse
