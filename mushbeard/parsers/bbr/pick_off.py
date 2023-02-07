import re

from ..helpers import grab_match_group
from ..models import create_find_match_request
from ..typing import ParserType, HandleType, MatchType


def handle_match(match: MatchType) -> HandleType:
    return {
        'type': grab_match_group(match, 1),
    }

def parse_pick_off() -> ParserType:
    expressions = [
        r'^ *.+? (picked off)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse
