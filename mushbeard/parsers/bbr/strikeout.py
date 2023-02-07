import re

from ..helpers import grab_match_group
from ..models import create_find_match_request
from ..typing import ParserType, HandleType, MatchType


def handle_match(match: MatchType) -> HandleType:
    if len(match.groups()) == 1:
        return {
            'type': grab_match_group(match, 1),
        }

    return {
        'type': grab_match_group(match, 1),
        'effort': grab_match_group(match, 2)
    }

def parse_strikeout() -> ParserType:
    expressions = [
        r'^ *(strikeout) (swinging|looking)',
        r'^ *(strikeout) \(?((?:foul|missed) bunt)\)?',
        r'^ *(strikeout) *$',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse
