import re

from ..helpers import grab
from ..models import create_find_match_request
from ..typing import ParserType, HandleType, MatchType


def handle_match(match: MatchType) -> HandleType:
    return {
        'type': grab(match, 0)
    }

def parse_wild_pitch() -> ParserType:
    expressions = [
        r'^ *(wild pitch)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_passed_ball() -> ParserType:
    expressions = [
        r'^ *(passed ball)'
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse
