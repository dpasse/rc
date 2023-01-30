import re

from .helpers import create_find_match_request
from .typing import ParserType, HandleType, MatchType


def handle_match(_: MatchType) -> HandleType:
    return {
        'type': 'Error',
    }

def parse_error() -> ParserType:
    expressions = [
        r'^ *reached on (e\d+)',
        r'^ *(e\d+) on',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse
