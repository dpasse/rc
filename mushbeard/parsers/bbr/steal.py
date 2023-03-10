import re

from ..helpers import grab_match_group
from ..models import create_find_match_request
from ..typing import ParserType, HandleType, MatchType


def handle_match(match: MatchType) -> HandleType:
    return {
        'type': grab_match_group(match, 1),
        'at': grab_match_group(match, 2),
    }

def parse_steal() -> ParserType:
    expressions = [
        r'^ *.+? (steals) (.+)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_caught_stealing() -> ParserType:
    expressions = [
        r'^ *.+? (caught stealing) (.+)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse
