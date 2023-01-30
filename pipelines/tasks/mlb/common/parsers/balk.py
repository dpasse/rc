import re

from .helpers import create_find_match_request, grab
from .typing import ParserType, HandleType, MatchType


def handle_match(match: MatchType) -> HandleType:
    return {
        'type': grab(match, 1),
    }

def parse_balk() -> ParserType:
    expressions = [
        r'^ *(balk)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse
