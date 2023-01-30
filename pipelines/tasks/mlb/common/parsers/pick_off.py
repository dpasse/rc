import re

from .helpers import create_find_match_request, grab
from .typing import ParseType, HandleType


def handle_match(match: re.Match[str]) -> HandleType:
    return {
        'type': grab(match, 1),
    }

def parse_pick_off() -> ParseType:
    expressions = [
        r'^ *.+? (picked off)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse
