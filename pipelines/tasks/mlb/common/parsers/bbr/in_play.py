import re

from ..helpers import grab
from ..models import create_find_match_request
from ..typing import ParserType, HandleType, MatchType


def handle_match(match: MatchType) -> HandleType:
    return {
        'type': grab(match, 1),
    }

def parse_ground_rule_double() -> ParserType:
    expressions = [
        r'^ *(ground-rule double)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_out_of_play_outs() -> ParserType:
    expressions = [
        r'^ *(foul (?:bunt |)(?:flyball|popfly|lineout))',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_in_play_outs() -> ParserType:
    expressions = [
        r'^ *((?:bunt )?(?:flyball|popfly|(?:line|ground)out))',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_in_play() -> ParserType:
    expressions = [
        r'^ *((?:intentional )?walk|hit by pitch|single|double|triple|home run|inside-the-park home run)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_fielders_choice() -> ParserType:
    expressions = [
        r"^ *(fielder's choice)",
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_reached_on() -> ParserType:
    expressions = [
        r"^ *reached on (interference)",
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse
