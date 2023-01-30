import re

from .helpers import create_find_match_request
from .typing import ParseType, HandleType


def handle_match(_: re.Match[str]) -> HandleType:
    return {
        'type': 'Error',
    }

def parse_error() -> ParseType:
    expressions = [
        r'^ *reached on (e\d+)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse
