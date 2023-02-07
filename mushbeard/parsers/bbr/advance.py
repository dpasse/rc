import re

from ..helpers import grab_match_group
from ..models import create_find_match_request
from ..typing import ParserType, HandleType, MatchType


def handle_advance_match(match: MatchType) -> HandleType:
    return {
        'player': grab_match_group(match, 1),
        'type': 'Advanced',
        'at': grab_match_group(match, 2),
    }

def parse_advance() -> ParserType:
    expressions = [
        r'^ *(.+?) to ([123]B) *$',
    ]

    return create_find_match_request(expressions, handle_advance_match, re.IGNORECASE).parse

def handle_out_advance_match(match: MatchType) -> HandleType:
    return {
        'type': grab_match_group(match, 1),
    }

def parse_out_advance() -> ParserType:
    expressions = [
        r'^ *baserunner (out advancing|advance) *$',
    ]

    return create_find_match_request(expressions, handle_out_advance_match, re.IGNORECASE).parse
